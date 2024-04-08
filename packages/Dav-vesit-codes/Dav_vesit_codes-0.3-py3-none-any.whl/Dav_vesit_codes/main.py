def acf(selection):
    switcher = {
        1: '''
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
        2: '''
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
        3: '''
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
        4: '''
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
        5: '''
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
            '''
    }

    return switcher.get(selection, "Invalid selection")

