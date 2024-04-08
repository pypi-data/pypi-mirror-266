def get_house():
    string ="""
    %%html
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
                fill: rgb;
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
    """
    return string