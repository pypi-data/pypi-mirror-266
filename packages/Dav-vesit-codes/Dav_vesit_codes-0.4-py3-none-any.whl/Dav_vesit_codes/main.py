def acf(selection):
    s= '''
            import numpy as np
            import pandas as pd
            import matplotlib.pylab as plt
            %matplotlib inline
            from matplotlib.pylab import rcParams
            from datetime import datetime

            df = pd.read_csv("/content/AirPassengers.csv")
            df.head(5)

            df.info()

            df.describe()

            from datetime import datetime
            df['Month'] = pd.to_datetime(df['Month'], infer_datetime_format=True)
            idf = df.set_index(['Month'])

            idf.head(5)

            idf.tail(5)

            plt.xlabel("Date")
            plt.ylabel("No of Passengers")
            plt.plot(idf)

            mean = idf.rolling(window=12).mean()
            std = idf.rolling(window=12).std()
            print(mean)
            print(std)

            orig = plt.plot(idf, color='blue', label='Original')
            mean_ = plt.plot(mean, color='red', label="Rolling Mean")
            std_ = plt.plot(std, color='black', label="Rolling Std")
            plt.legend(loc="best")

            #ADF
            from statsmodels.tsa.stattools import adfuller
            print("Results of Dickey Fuller Test")
            # Here AIC helps to analyse the exact value from actual values and difference between them
            dftest = adfuller(idf['#Passengers'], autolag='AIC')
            dfoutput = pd.Series(dftest[0:4],index=['Test statistic','p-value','#Lags used','No. of observations used'])
            for key, value in dftest[4].items():
            dfoutput['Critical value (%s)'%key]= value

            print(dfoutput)

            indexedDataset_logScale = np.log(idf)
            plt.plot(indexedDataset_logScale)

            from statsmodels.tsa.stattools import adfuller
            def test_stationarity(timeSeries):
            # Determinig Rolling statistics
            movingaverage = timeSeries.rolling(window=12).mean()
            movingSTD = timeSeries.rolling(window=12).std()

            # Plot rolling statistics
            orig = plt.plot(timeSeries, color = 'blue', label = "Original")
            mean = plt.plot(movingaverage, color = 'red', label = "Rolling Mean")
            std = plt.plot(movingSTD, color = 'black', label = "Rolling Std")
            plt.legend(loc = "best")
            plt.title("Rolling Mean & Standard Deviation")
            plt.show()

            # Perform Dickey-Fuller Test
            print("Results of Dickey Fuller Test")
            dftest = adfuller(timeSeries['#Passengers'], autolag='AIC')
            dfoutput = pd.Series(dftest[0:4],index=['Test statistic','p-value','#Lags used','No. of observations used'])
            for key, value in dftest[4].items():
                dfoutput['Critical value (%s)'%key]= value
            print(dfoutput)

            # Transformation-1:Subtracting MA from LogScale Data
            movingaverage = indexedDataset_logScale.rolling(window=12).mean()
            movingSTD = indexedDataset_logScale.rolling(window=12).mean()
            plt.plot(indexedDataset_logScale)
            plt.plot(movingaverage,color='red')

            dataLogScaleMinusMovingAverage = indexedDataset_logScale - movingaverage
            dataLogScaleMinusMovingAverage.head(12)

            dataLogScaleMinusMovingAverage.dropna(inplace=True)
            dataLogScaleMinusMovingAverage.head(18)

            test_stationarity(dataLogScaleMinusMovingAverage)

            #Subtrating Exponential Decay Weighted Average from LogScale Data

            exponentialDecayWeightedAverage = indexedDataset_logScale.ewm(halflife=12,min_periods=0, adjust=True).mean()
            plt.plot(indexedDataset_logScale)
            plt.plot(exponentialDecayWeightedAverage,color='red')

            datasetLogScaleMinusMovingExponentialDecayAverage = indexedDataset_logScale - exponentialDecayWeightedAverage

            test_stationarity(datasetLogScaleMinusMovingExponentialDecayAverage)

            #Components
            
            from statsmodels.tsa.seasonal import seasonal_decompose
            decomposition = seasonal_decompose(indexedDataset_logScale)
            trend = decomposition.trend
            seasonal = decomposition.seasonal
            residual = decomposition.resid
            plt.subplot(411)
            plt.plot(indexedDataset_logScale, label = 'Original')
            plt.legend(loc='best')
            plt.subplot(412)
            plt.plot(trend,label='Trend')
            plt.legend(loc='best')
            plt.subplot(413)
            plt.plot(seasonal,label='Seasonality')
            plt.legend(loc='best')
            plt.subplot(414)
            plt.plot(residual,label='Residuals')
            plt.legend(loc='best')
            plt.tight_layout()

            decomposedLogData = residual
            decomposedLogData.dropna(inplace = True)
            print(decomposedLogData)

            decomposedLogData.describe()

            decomposedLogData.head(12)

            test_stationarity(decomposedLogData)

            #a.ACF and PACF
            from statsmodels.graphics.tsaplots import plot_pacf, plot_acf
            pacf=plot_pacf(datasetLogScaleMinusMovingExponentialDecayAverage,lags=10)
            acf=plot_acf(datasetLogScaleMinusMovingExponentialDecayAverage,lags=10)

            #Split the logscale data for training and testing
            train=datasetLogScaleMinusMovingExponentialDecayAverage[:len(datasetLogScaleMinusMovingExponentialDecayAverage)-60]
            test=datasetLogScaleMinusMovingExponentialDecayAverage[len(datasetLogScaleMinusMovingExponentialDecayAverage)-60:]

            c.Train the AR Model
            from statsmodels.tsa.ar_model import AutoReg
            # AR Model with p = 2 from PACF plot
            model_1 = AutoReg(train, lags=1).fit()

            print(model_1.summary())

            pred=model_1.predict(start=len(train),end=len(datasetLogScaleMinusMovingExponentialDecayAverage)-1, dynamic=False)
            
            print(len(train))
            print(pred)

            from math import sqrt
            from sklearn.metrics import mean_squared_error
            rmse=sqrt(mean_squared_error(test,pred))
            print(rmse)

            pred_future=model_1.predict(start=len(datasetLogScaleMinusMovingExponentialDecayAverage)+1, end=len(datasetLogScaleMinusMovingExponentialDecayAverage)+60, dynamic=False)
            print("Prediction for next 5 years")
            print(pred_future)
            print("No. of predictions : \t", len(pred_future))

            #d = 1

            datasetLogDiffShifting = indexedDataset_logScale - indexedDataset_logScale.shift()
            plt.plot(datasetLogDiffShifting)

            datasetLogDiffShifting.dropna(inplace=True)
            test_stationarity(datasetLogDiffShifting)

            # a.2. To find p and q values

            from statsmodels.tsa.stattools import acf, pacf
            lag_acf = acf(datasetLogScaleMinusMovingExponentialDecayAverage, nlags=20)
            lag_pacf = pacf(datasetLogScaleMinusMovingExponentialDecayAverage,nlags=20, method='ols')

            #Plot ACF
            plt.subplot(121)
            plt.plot(lag_acf)
            plt.axhline(y=0, linestyle='--',color='grey')
            plt.axhline(y=-1.96/np.sqrt(len(datasetLogScaleMinusMovingExponentialDecayAverage)), linestyle='--', color='gray')
            plt.axhline(y=1.96/np.sqrt(len(datasetLogScaleMinusMovingExponentialDecayAverage)), linestyle='--', color='gray')
            plt.title("Autocorrelation Function")

            #Plot PACF
            plt.subplot(122)
            plt.plot(lag_pacf)
            plt.axhline(y=0, linestyle='--',color='grey')
            plt.axhline(y=-1.96/np.sqrt(len(datasetLogScaleMinusMovingExponentialDecayAverage)), linestyle='--', color='gray')
            plt.axhline(y=1.96/np.sqrt(len(datasetLogScaleMinusMovingExponentialDecayAverage)), linestyle='--', color='gray')
            plt.title("Partial Autocorrelation Function")
            plt.tight_layout()

            p = 2 , q = 2 and d = 1

            # b. Compute the models

            # AR Model using ARIMA package

            from statsmodels.tsa.arima.model import ARIMA
            # AR Model
            model_0 = ARIMA(datasetLogScaleMinusMovingExponentialDecayAverage, order=(2,0,0))
            results_AR = model_0.fit()
            print(results_AR.fittedvalues)
            print('RSS: %f' % sum((results_AR.fittedvalues-datasetLogScaleMinusMovingExponentialDecayAverage['#Passengers'])**2))
            plt.plot(datasetLogScaleMinusMovingExponentialDecayAverage)
            plt.plot(results_AR.fittedvalues, color='red')
            plt.title('RSS: %.4f' % sum((results_AR.fittedvalues-datasetLogScaleMinusMovingExponentialDecayAverage['#Passengers'])**2))
            print("Plotting AR Model")

            # MA Model using ARIMA package

            from statsmodels.tsa.arima.model import ARIMA
            # MA Model
            model_0 = ARIMA(datasetLogScaleMinusMovingExponentialDecayAverage, order=(0,0,2))
            results_MA = model_0.fit()
            print(results_MA.fittedvalues)
            print('RSS: %f' % sum((results_MA.fittedvalues-datasetLogScaleMinusMovingExponentialDecayAverage['#Passengers'])**2))
            plt.plot(datasetLogScaleMinusMovingExponentialDecayAverage)
            plt.plot(results_MA.fittedvalues, color='red')
            plt.title('RSS: %.4f' % sum((results_MA.fittedvalues-datasetLogScaleMinusMovingExponentialDecayAverage['#Passengers'])**2))
            print("Plotting MA Model")

            # ARMA Model using ARIMA package

            from statsmodels.tsa.arima.model import ARIMA
            # ARMA Model
            model_03 = ARIMA(datasetLogScaleMinusMovingExponentialDecayAverage, order=(2,0,2))
            results_ARMA = model_03.fit()
            print(results_ARMA.fittedvalues)
            print('RSS: %f' % sum((results_ARMA.fittedvalues-datasetLogScaleMinusMovingExponentialDecayAverage['#Passengers'])**2))
            plt.plot(datasetLogScaleMinusMovingExponentialDecayAverage)
            plt.plot(results_ARMA.fittedvalues, color='red')
            plt.title('RSS: %.4f' % sum((results_ARMA.fittedvalues-datasetLogScaleMinusMovingExponentialDecayAverage['#Passengers'])**2))
            print("Plotting ARMA Model")

            # ARIMA Model using ARIMA package

            from statsmodels.tsa.arima.model import ARIMA
            # ARIMA Model
            model_1 = ARIMA(datasetLogScaleMinusMovingExponentialDecayAverage, order=(2,1,2))
            results_ARIMA = model_1.fit()
            print(results_ARIMA.fittedvalues)
            print('RSS: %f' % sum((results_ARIMA.fittedvalues-datasetLogScaleMinusMovingExponentialDecayAverage['#Passengers'])**2))
            print("Plotting ARIMA Model")
        '''
    switcher = {
        0: '''
           1 Draw the Simple Linear Regression line for the given dataset in Python. 
           2 Draw the Multiple Linear Regression line for the given dataset in Python
           3 Draw the Simple Linear Regression line for the given dataset in R
           4 Draw the Multiple Linear Regression line for the given dataset in R
           5 Decompose the given time Series Data in Python for the given dataset. Plot the ACF and PACF graphs for the given dataset.
           6 Implement ARIMA Model in Python for the given dataset
           7 Implement AR Model in Python for the given dataset
           8 Implement MA Model in Python for the given dataset
            9 Draw a House using D3.js

            10 Draw an Indian Flag using D3.js
            11 Draw random circles of different sizes and colors using D3.js
            12 Draw any three shapes and label them using D3.js
            13 Implement a Timer using D3.js
            14 Draw a rectangle and rotate it about an axis using D3.js
            15 Perform EDA using Matplotlib for the given dataset
            16 Perform EDA using seaborne for the given dataset
            17 Perform EDA using plotly for the given dataset
            18 Perform EDA using ggplot2 for the given dataset

        ''',
        1: '''import numpy as np
            import pandas as pd
            import seaborn as sns
            import matplotlib.pyplot as plt

            df = pd.read_csv("/content/Simple linear regression.csv")
            df.head(5)

            df.info()

            df.describe()

            df.isnull().mean()*100

            df.corr()

            correlation_matrix = df.corr()

            plt.figure(figsize=(8,6))
            sns.heatmap(correlation_matrix,annot= True,cmap='coolwarm',fmt=".3f" )
            plt.show()

            X = df['SAT']
            y = df['GPA']

            from sklearn.model_selection import train_test_split
            X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=0.3,random_state=33)

            X_train = np.array(X_train).reshape(-1,1)

            X_train

            X_test = np.array(X_test).reshape(-1,1)

            X_test

            from sklearn.linear_model import LinearRegression
            lr = LinearRegression()
            lr.fit(X_train,y_train)

            y_pred = lr.predict(X_test)

            y_pred

            m = lr.coef_
            c = lr.intercept_
            print(m)
            print(c)

            plt.scatter(X_test,y_test)
            plt.plot(X_test,y_pred,color="red")

            print(f"Equation of line : GPA = {m[0]:.8f} * SAT + {c:.8f}")
            ''',
        2: '''
            import numpy as np
            import pandas as pd
            import matplotlib.pyplot as plt
            import seaborn as sns

            df = pd.read_csv('/content/data.csv')
            df.head(5)

            df.info()

            df.describe()

            df.shape

            df_numeric = df.drop(columns=['Car','Model'])

            df_numeric.corr()

            X = df[['Volume','Weight']]
            y = df['CO2']

            fig , axs = plt.subplots(2,figsize=(5,5))
            plt1 = sns.boxplot(df['Weight'],ax=axs[0])
            plt2 = sns.boxplot(df['Volume'],ax=axs[1])
            plt.tight_layout()

            sns.distplot(df['CO2'])

            sns.pairplot(df,x_vars=['Weight','Volume'],y_vars='CO2',height=4,aspect=1,kind='scatter')
            plt.show()

            sns.heatmap(df_numeric.corr(),annot=True,cmap='coolwarm')

            from sklearn.model_selection import train_test_split, cross_val_score

            X_train,X_test,y_train,y_test = train_test_split(X,y,test_size = 0.3,random_state=100)

            from sklearn.linear_model import LinearRegression

            y_test.shape

            y_train.shape

            lr = LinearRegression()
            lr.fit(X_train,y_train)

            print(f"Intercept = {lr.intercept_}")
            list(zip(X,lr.coef_))

            y_pred = lr.predict(X_test)

            reg_model_diff = pd.DataFrame({'Actual Value':y_test,'Predicted Value':y_pred})
            reg_model_diff

            from sklearn.metrics import mean_squared_error, mean_absolute_error

            mae = mean_absolute_error(y_test,y_pred)
            mse = mean_squared_error(y_test,y_pred)
            r2 = np.sqrt(mean_squared_error(y_test,y_pred))

            print('Mean Absolute Error:', mae)
            print('Mean Square Error:', mse)
            print('Root Mean Square Error:', r2)

            from mpl_toolkits.mplot3d import Axes3D

            # Create a new figure and axis
            fig = plt.figure(figsize=(10, 8))
            ax = fig.add_subplot(111, projection='3d')

            # Plot the actual data points
            ax.scatter(X_test['Volume'], X_test['Weight'], y_test, color='blue', label='Actual')

            # Predict CO2 values for a mesh grid of Volume and Weight values
            x1, x2 = np.meshgrid(np.linspace(X_test['Volume'].min(), X_test['Volume'].max(), 10),
                                np.linspace(X_test['Weight'].min(), X_test['Weight'].max(), 10))
            y_pred_mesh = lr.predict(np.array([x1.flatten(), x2.flatten()]).T).reshape(x1.shape)

            # Plot the surface representing the regression plane
            ax.plot_surface(x1, x2, y_pred_mesh, alpha=0.5, color='red', label='Regression Plane')

            # Set axis labels
            ax.set_xlabel('Volume')
            ax.set_ylabel('Weight')
            ax.set_zlabel('CO2')

            # Show the plot
            plt.show()

            print("Equation of the line:")
            print("CO2 =", lr.intercept_, "+", lr.coef_[0], "* Volume +", lr.coef_[1], "* Weight")
            ''',
        3: '''
            data = read.csv("/content/Salary_Data.csv" , header = T)

            library(tidyverse)
            library(caret)
            library(MASS)
            library(lmtest)
            library(olsrr)
            library(broom)

            sample_n(data,5)

            plot(data$YearsExperience,data$Salary)

            cor.test(data$YearsExperience , data$Salary)

            # Install and load the caret package
            install.packages("caret")
            library(caret)

            # Set seed for reproducibility
            set.seed(123)

            # Create training samples
            training.samples <- createDataPartition(data$Salary, p = 0.6, list = FALSE)

            # Split data into training and test sets
            train.data <- data[training.samples, ]
            test.data <- data[-training.samples, ]

            # Fit model
            model <- lm(Salary ~ YearsExperience, data = train.data)

            # Print summary of the model
            summary(model)


            # Normality Assumption

            qqnorm(model$residuals)
            qqline(model$residuals , col = "steelblue", lwd = 2)

            # Statistical Test
            shapiro.test(model$residuals)

            # Homoscadasticity assumption by -

            install.packages("lmtest")
            library(lmtest)

            # Visualization
            plot(model$fitted.values , model$residuals)

            # Statistical Test
            bptest(model)

            # Errors have a constant variance

            # Making prediction
            prediction <- model %>% predict(test.data)

            # Visualization
            plot(test.data$Salary , prediction)
            abline(lm(prediction ~ Salary, data = test.data), col = "blue")

            # Statistical Measure
            data.frame( R2 = R2(prediction, test.data$Salary),
                        RMSE = RMSE(prediction, test.data$Salary),
                        MAE = MAE(prediction, test.data$Salary))

            # Extract coefficients from the model
            intercept <- coef(model)[1]
            coefficient_years_experience <- coef(model)[2]

            # Print the equation of the line
            cat("Equation of the line: Salary =", intercept, "+", coefficient_years_experience, "* YearsExperience\n")
            ''',
        4: '''
            install.packages("caret")
            install.packages('corrplot')

            library(ggplot2)
            library(dplyr)
            library(tidyverse)
            library(caret)
            library(corrplot)

            Data <- read.csv("/content/company.csv")

            x.cor <- cor(Data)
            x.cor

            heatmap(x = x.cor, symm = TRUE)

            pairs(Data)

            hist_plot <- ggplot(Data, aes(x = Sales)) +
            geom_histogram(color = "black", fill = "blue", bins = 24) +
            labs(title = "Histogram of Sales")
            print(hist_plot)

            set.seed(42)
            train_index <- createDataPartition(Data$Sales, p = 0.75, list = FALSE)
            x_train <- subset(Data, rownames(Data) %in% train_index, select = c("Sales", "TV", "Radio"))
            x_test <- subset(Data, !(rownames(Data) %in% train_index), select = c("Sales", "TV", "Radio"))

            model <- lm(Sales ~ ., data = x_train)
            summary(model)

            x_train <- x_train[c("TV","Radio")]
            x_test <- x_test[c("TV","Radio")]
            y_train <- x_train["Sales"]
            y_test <- x_test["Sales"]

            x_test <- data.frame(TV = x_test["TV"], Radio = x_test["Radio"])

            y_predict <- predict(model, newdata = x_test)

            install.packages('plot3D')

            library("plot3D")

            # set the x, y, and z variables
            x <- Data$Radio
            y <- Data$TV
            z <- Data$Sales

            # Compute the linear regression
            fit <- lm(z ~ x + y)

            # create a grid from the x and y values (min to max) and predict values for every point
            # this will become the regression plane
            grid.lines = 40
            x.pred <- seq(min(x), max(x), length.out = grid.lines)
            y.pred <- seq(min(y), max(y), length.out = grid.lines)
            xy <- expand.grid( x = x.pred, y = y.pred)
            z.pred <- matrix(predict(fit, newdata = xy),
                            nrow = grid.lines, ncol = grid.lines)

            # create the fitted points for droplines to the surface
            fitpoints <- predict(fit)

            scatter3D(x, y, z, pch = 17, col="red",
                    theta = 45, phi = 0,
                    ticktype = "detailed",
                    xlab = "Radio", ylab = "TV", zlab = "Sales",
                    surf = list(x = x.pred, y = y.pred, z = z.pred,
                                facets = TRUE, fit = fitpoints, col = ramp.col (col = c("dodgerblue3","seagreen2"),
                                                                                n = 10, alpha = 0.9), border = "black"),
                    main = "Data")

            # Extract coefficients from the model
            intercept <- coef(fit)[1]
            coefficient_radio <- coef(fit)["x"]
            coefficient_tv <- coef(fit)["y"]

            # Print the equation of the plane
            cat("Equation of the plane: Sales =", intercept, "+", coefficient_radio, "* Radio +", coefficient_tv, "* TV\n")
        ''',
        5:s,
        6:s,
        7:s,
        8:s,
        9: '''
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Simple House Drawing using D3.js</title>
                <script src="https://d3js.org/d3.v7.min.js"></script>
                <style>
                    .roof {
                        fill: #d9534f;
                    }
                    .wall {
                        fill: ;
                    }
                    .door {
                        fill: #5cb85c;
                    }
                    .window {
                        fill: #f0ad4e;
                    }
                </style>
            </head>
            <body>
                <svg width="400" height="400"></svg>

                <script>
                    const svg = d3.select("svg");

                    // Draw the roof
                    svg.append("polygon")
                        .attr("points", "50,100 200,10 350,100")
                        .attr("class", "roof");

                    // Draw the walls
                    svg.append("rect")
                        .attr("x", 50)
                        .attr("y", 100)
                        .attr("width", 300)
                        .attr("height", 350)
                        .attr("class", "wall");

                    // Draw the door
                    svg.append("rect")
                        .attr("x", 175)
                        .attr("y", 300)
                        .attr("width", 50)
                        .attr("height", 100)
                        .attr("class", "door");

                    // Draw the window1
                    svg.append("rect")
                        .attr("x", 85)
                        .attr("y", 150)
                        .attr("width", 75)
                        .attr("height", 75)
                        .attr("class", "window");

                    // Draw the window2
                    svg.append("rect")
                        .attr("x", 240)
                        .attr("y", 150)
                        .attr("width", 75)
                        .attr("height", 75)
                        .attr("class", "window");

                </script>
            </body>
            </html>
            ''',
        10: '''
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Indian Flag</title>
                <script src="https://d3js.org/d3.v7.min.js"></script>
                <style>
                    rect {
                        stroke-width: 0;
                    }
                </style>
            </head>
            <body>
                <svg width="600" height="400"></svg>
                <script>
                    const svg = d3.select("svg");

                    // Colors
                    const saffron = "#FF9933";
                    const white = "#FFFFFF";
                    const green = "#138808";
                    const navyBlue = "#000080";

                    // Dimensions
                    const width = 600;
                    const height = 300;

                    // Stripe heights
                    const stripeHeight = height / 3;
                    const chakraRadius = stripeHeight / 8;

                    svg.append("rect")
                        .attr("width", 50)
                        .attr("height", 1000)
                        .attr("fill", "#994B00")
                        .attr("x", 0)
                        .attr("y", 0);
                    // Draw Saffron Stripe
                    svg.append("rect")
                        .attr("width", width)
                        .attr("height", stripeHeight)
                        .attr("fill", saffron)
                        .attr("x", 50)
                        .attr("y", 0);

                    // Draw White Stripe
                    svg.append("rect")
                        .attr("width", width)
                        .attr("height", stripeHeight)
                        .attr("fill", white)
                        .attr("x", 50)
                        .attr("y", stripeHeight);

                    // Draw Green Stripe
                    svg.append("rect")
                        .attr("width", width)
                        .attr("height", stripeHeight)
                        .attr("fill", green)
                        .attr("x", 50)
                        .attr("y", stripeHeight * 2);

                    // Draw Navy Blue Chakra
                    const chakraX = width / 2;
                    const chakraY = height / 2;
                    svg.append("circle")
                        .attr("cx", chakraX)
                        .attr("cy", chakraY)
                        .attr("r", 50)
                        .attr("fill", navyBlue);


                </script>
            </body>
            </html>
            ''',
        11: '''
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Random Circles</title>
                <script src="https://d3js.org/d3.v7.min.js"></script>
            </head>
            <body>
                <svg width="800" height="600"></svg>
                <script>
                    const svg = d3.select("svg");

                    const numCircles = 10; // Number of circles to draw

                    // Random function to generate different sizes and colors
                    const randomColor = () => {
                        return '#' + Math.floor(Math.random()*16777215).toString(16); // Random color hex code
                    }

                    const randomSize = () => {
                        return Math.random() * 30 + 30; // Random size between 10 and 60
                    }

                    // Draw random circles
                    for (let i = 0; i < numCircles; i++) {
                        const cx = Math.random() * 600 +100; // Random x-coordinate within SVG width
                        const cy = Math.random() * 400 +100; // Random y-coordinate within SVG height
                        const radius = randomSize(); // Random radius
                        const color = randomColor(); // Random color

                        svg.append("circle")
                            .attr("cx", cx)
                            .attr("cy", cy)
                            .attr("r", radius)
                            .attr("fill", color)
                            .attr("opacity", 0.7); // Adjust opacity for better visibility
                    }
                </script>
            </body>
            </html>
            ''',
        12: '''
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Shapes with Labels</title>
                <script src="https://d3js.org/d3.v7.min.js"></script>
            </head>
            <body>
                <svg width="400" height="200"></svg>
                <script>
                    const svg = d3.select("svg");

                    svg.append("rect")
                        .attr("x", 50)
                        .attr("y", 50)
                        .attr("width", 100)
                        .attr("height", 50)
                        .attr("fill", "lightblue");
                
                    svg.append("circle")
                        .attr("cx", 220)
                        .attr("cy", 100)
                        .attr("r", 30)
                        .attr("fill", "lightgreen");

                    svg.append("ellipse")
                        .attr("cx", 320)
                        .attr("cy", 150)
                        .attr("rx", 50)
                        .attr("ry", 30)
                        .attr("fill", "lightcoral");

                    // Labels
                    svg.append("text")
                        .attr("x", 100)
                        .attr("y", 75)
                        .attr("text-anchor", "middle")
                        .attr("alignment-baseline", "middle")
                        .text("Rectangle");

                    svg.append("text")
                        .attr("x", 220)
                        .attr("y", 115)
                        .attr("text-anchor", "middle")
                        .attr("alignment-baseline", "middle")
                        .text("Circle");

                    svg.append("text")
                        .attr("x", 320)
                        .attr("y", 160)
                        .attr("text-anchor", "middle")
                        .attr("alignment-baseline", "middle")
                        .text("Ellipse");
                </script>
            </body>
            </html>
            ''',
        13: '''
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>D3.js Stopwatch</title>
                <script src="https://d3js.org/d3.v7.min.js"></script>
                <style>
                    body {
                        background-color: #f2f2f2;
                    }

                    #stopwatch {
                        padding: 20px;
                        border-radius: 10px;
                        background-color: #ffffff;
                        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    }

                    .button {
                        margin: 5px;
                        padding: 10px 20px;
                        background-color: #007bff;
                        color: #fff;
                        border: none;
                        cursor: pointer;
                        transition: background-color 0.3s;
                    }

                    .button:hover {
                        background-color: #0056b3;
                    }

                    #display {
                        background-color: #000000;
                        color: #fff;
                        padding: 10px;
                        border-radius: 5px;
                        font-size: 24px;
                        margin-bottom: 10px;
                    }
                </style>
            </head>
            <body>
                <div id="stopwatch">
                    <span id="display">00:00:00</span><br>
                    <br>
                    <button id="start" class="button">Start</button>
                    <button id="stop" class="button">Stop</button>
                    <button id="reset" class="button">Reset</button>
                </div>

                <script>

                    let timer;
                    let startTime;
                    let running = false;
                    let elapsedTime = 0;

                    const display = d3.select("#display");
                    const startButton = d3.select("#start");
                    const stopButton = d3.select("#stop");
                    const resetButton = d3.select("#reset");

                    function formatTime(milliseconds) {
                        const totalSeconds = Math.floor(milliseconds / 1000);
                        const minutes = Math.floor(totalSeconds / 60).toString().padStart(2, '0');
                        const seconds = (totalSeconds % 60).toString().padStart(2, '0');
                        const ms = Math.floor((milliseconds % 1000) / 10).toString().padStart(2, '0');
                        return `${minutes}:${seconds}:${ms}`;
                    }

                    function updateDisplay() {
                        display.text(formatTime(elapsedTime));
                    }

                    function handleMouseOver() {
                        display.style("font-size", "50px");
                    }

                    function handleMouseOut() {
                        display.style("font-size", "24px");
                    }

                    display.on("mouseover", handleMouseOver)
                        .on("mouseout", handleMouseOut);

                    startButton.on("click", function() {
                        if (!running) {
                            startTime = Date.now() - elapsedTime;
                            timer = setInterval(function() {
                                elapsedTime = Date.now() - startTime;
                                updateDisplay();
                            }, 10);
                            running = true;
                            display.style("background-color", "#28a745");
                            display.style("color", "#ffffff");
                        }
                    });

                    stopButton.on("click", function() {
                        if (running) {
                            clearInterval(timer);
                            running = false;
                            display.style("background-color", "#FF0000");
                            display.style("color", "#ffffff");
                        }
                    });

                    resetButton.on("click", function() {
                        clearInterval(timer);
                        running = false;
                        elapsedTime = 0;
                        updateDisplay();
                        display.style("background-color", "#000000");
                        display.style("color", "#ffffff");
                    });

                    updateDisplay();
                </script>
            </body>
            </html>
            ''',
        14: '''
            %%html
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Rectangle Rotation using D3.js</title>
                <script src="https://d3js.org/d3.v7.min.js"></script>
            </head>
            <body>
                <svg width="400" height="400"></svg>

                <script>
                    const svg = d3.select("svg");

                    // Define initial rectangle properties
                    const rectWidth = 100;
                    const rectHeight = 50;
                    const initialX = 150;
                    const initialY = 150;

                    // Draw the rectangle
                    const rectangle = svg.append("rect")
                        .attr("x", initialX)
                        .attr("y", initialY)
                        .attr("width", rectWidth)
                        .attr("height", rectHeight)
                        .attr("fill", "lightblue");

                    // Define rotation properties
                    let rotationAngle = 180; 

                    function rotateRectangle() {

                        const rotationCenterX = initialX + rectWidth / 2;
                        const rotationCenterY = initialY + rectHeight / 2;

                        rectangle.attr("transform", `rotate(${rotationAngle}, ${rotationCenterX}, ${rotationCenterY})`);

                        rotationAngle += 1; 
                    }

                    setInterval(rotateRectangle, 50); 
                </script>
            </body>
            </html>
            ''',
        15: '''
            import numpy as np
            import pandas as pd
            import matplotlib.pyplot as plt

            data = pd.read_csv('pokemon.csv')
            data.head()

            data.columns

            # Line Plots

            plt.plot(data[["#"]][0:100], data[["Defense"]][0:100], label="line L")
            plt.plot(data[["#"]][0:100], data[["Attack"]][0:100], label="line H")
            plt.plot()
            plt.legend(loc='upper right')     # legend = puts label into plot
            plt.xlabel('x axis')              # label = name of label
            plt.ylabel('y axis')
            plt.title('Line Plot')            # title = title of plot
            plt.show()

            # Bar Plot

            plt.bar(data[["#"]][0:100].values.flatten(), data[["Defense"]][0:100].values.flatten(), label="Blue Bar", color='b')
            plt.plot()

            plt.xlabel("bar number")
            plt.ylabel("bar height")
            plt.title("Bar Chart Example")
            plt.legend()
            plt.show()

            # Histograms

            data.Speed.plot(kind='hist', bins=50, figsize=(12, 12))
            plt.show()

            # Scatter Plot

            plt.scatter(data[["Defense"]][0:100], data[["Attack"]][0:100], color='red')
            plt.xlabel('Attack')              # label = name of label
            plt.ylabel('Defence')
            plt.title('Attack Defense Scatter Plot')
            plt.show()

            # Stack Plot

            plt.plot([], [], color='r', label='D 1')
            plt.plot([], [], color='g', label='D 2')
            plt.plot([], [], color='b', label='D 3')

            plt.stackplot(data[["#"]][0:100].values.flatten(), data[["Defense"]][0:100].values.flatten(), data[["Attack"]][0:100].values.flatten(), data[["HP"]][0:100].values.flatten(), colors=['r', 'g', 'b'])
            plt.title('Stack Plot Example')
            plt.legend()
            plt.show()

            # 3D Scatter Plot

            import matplotlib.pyplot as plt
            import numpy as np
            from mpl_toolkits.mplot3d import axes3d

            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')

            x1 = data[["#"]][0:100].values.flatten()
            y1 = data[["Defense"]][0:100].values.flatten()
            z1 = data[["Attack"]][0:100].values.flatten()

            ax.scatter(x1, y1, z1, c='b', marker='o', label='blue')

            ax.set_xlabel('x axis')
            ax.set_ylabel('y axis')
            ax.set_zlabel('z axis')
            plt.title("3D Scatter Plot Example")
            plt.legend()
            plt.tight_layout()
            plt.show()
        ''',
        16: '''
        import numpy as np
        import pandas as pd
        import seaborn as sns

        data = pd.read_csv('pokemon.csv')
        data.head()

        data.columns

        # Assuming 'data' is your DataFrame
        sns.pairplot(data[['HP', 'Attack', 'Defense', 'Speed']])
        plt.show()


        selected_types = ['Grass', 'Fire', 'Water', 'Electric', 'Psychic']
        filtered_data = data[data['Type 1'].isin(selected_types)]

        sns.violinplot(x='Type 1', y='HP', data=filtered_data)
        plt.xlabel('Type 1')
        plt.ylabel('HP')
        plt.title('HP Distribution by Type 1')
        plt.show()

        sns.boxplot(x='Legendary', y='Attack', data=data)
        plt.xlabel('Legendary')
        plt.ylabel('Attack')
        plt.title('Attack Distribution by Legendary Status')
        plt.show()

        sns.heatmap(data[['HP', 'Attack', 'Defense', 'Speed']].corr(), annot=True, cmap='coolwarm')
        plt.title('Correlation Heatmap')
        plt.show()

        sns.lineplot(x='Speed', y='Attack', hue='Type 1', data=filtered_data)
        plt.xlabel('Speed')
        plt.ylabel('Attack')
        plt.title('Attack vs Speed by Type 1')
        plt.legend(loc='upper right')
        plt.show()
        ''',
        17: '''
            #IN PYTHON
            import plotly.express as px

            fig = px.scatter(data, x='Attack', y='Defense', color='Type 1', title='Attack vs Defense',
                            hover_data=['Name', 'Type 1'])
            fig.show()

            fig = px.histogram(data, x='HP', title='HP Distribution',
                            labels={'HP': 'HP', 'count': 'Count'})
            fig.show()

            fig = px.box(data, x='Legendary', y='Attack', title='Attack Distribution by Legendary Status',
                        labels={'Attack': 'Attack', 'Legendary': 'Legendary'})
            fig.show()

            type1_distribution = data['Type 1'].value_counts()

            fig = px.pie(names=type1_distribution.index, values=type1_distribution.values,
                        title='Distribution of Pokémon by Type 1')
            fig.show()

            selected_types = ['Grass', 'Fire', 'Water', 'Electric', 'Psychic']

            # Filter the data for the selected types
            filtered_data = data[data['Type 1'].isin(selected_types)]

            # Calculate the value counts of each Pokémon type in the filtered data
            type1_distribution = filtered_data['Type 1'].value_counts()

            # Create a bar plot using Plotly
            fig = px.bar(x=type1_distribution.index, y=type1_distribution.values,
                        labels={'x': 'Type 1', 'y': 'Count'},
                        title='Count of Pokémon by Type 1 (Filtered)',color=type1_distribution.index)
            fig.show()


            #IN R
            df <- read.csv("pokemon.csv")

            head(df)

            str(df)

            summary(df)

            colMeans(is.na(df))

            print(colnames(df))

            selected_columns <- c("Attack","Defense","Sp..Atk","Sp..Def","Speed")
            cor(df[selected_columns])

            install.packages("plotly")

            library(plotly)

            scatter_plot <- plot_ly(df, x = ~Attack, y = ~Defense, type = 'scatter', mode = 'markers')
            scatter_plot

            histogram_plot <- plot_ly(df, x = ~HP, type = 'histogram')
            histogram_plot

            box_plot <- plot_ly(df, x = ~Legendary, y = ~Attack, type = 'box')
            box_plot

            bar_plot <- plot_ly(df, x = ~Type.1, type = 'bar')
            bar_plot

            line_plot <- plot_ly(df, x = ~Speed, y = ~Attack, type = 'scatter', mode = 'lines', color = ~Type.1)
            line_plot
        ''',
        18:'''
        data <- read.csv("pokemon.csv")
        head(df)

        str(df)

        summary(df)

        colMeans(is.na(df))

        print(colnames(df))

        library(ggplot2)

        ggplot(data, aes(x=Attack, y=Defense)) +
        geom_point()

        ggplot(data, aes(x=HP)) +
        geom_histogram()

        ggplot(data, aes(x=Legendary, y=Attack)) +
        geom_boxplot()

        ggplot(data, aes(x=Type.1)) +
        geom_bar()

        ggplot(data, aes(x=Speed, y=Attack, color=Type.1)) +
        geom_line()

        pairs(~ Attack + Defense + HP + Speed, data=data,
            main="Pairplot of Pokémon Stats")

'''
    }

    return switcher.get(selection, "Invalid selection")


