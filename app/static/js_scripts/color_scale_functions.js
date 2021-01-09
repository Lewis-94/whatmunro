    function updateCircleColours(){
        selectedOption = d3.select("#selectButton").property("value");
        var bounds = getBounds(selectedOption);
        var colors = getColors(selectedOption);
        var myColors = d3.scaleLinear().domain(bounds).range(colors)

        var sliderVal = sliderSimple.value()
        svgCircles.selectAll("circle")
        .style("fill", function(d,i) {return myColors(d[selectedOption][sliderVal])});
    }

    function updateScale(){

        selectedOption = d3.select("#selectButton").property("value");
        var bounds = getBounds(selectedOption);
        var colors = getColors(selectedOption);
        updateColourScale(bounds, colors);
    }

    function getBounds(selectedOption){

            var scale_type = "absolute";

            var maxes = [];
            var mins = [];
             svgCircles.selectAll("circle").each(
                function(d){
                maxes.push(d3.max(d[selectedOption]))
                mins.push(d3.min(d[selectedOption]))});

            var max = d3.max(maxes);
            var min = d3.min(mins);
            bounds = [min, (min+max)/2, max];

            if (selectedOption == "temp" || selectedOption == "feels_like"){
               if (scale_type == "absolute"){
                    bounds = [-30, 0, 30];
               } else {
                    if (bounds[0] < 0 && bounds[2] > 0){
                        bounds = [bounds[0], 0, bounds[2]];
                    } else if (bounds[0] > 0) {
                        bounds = [0, bounds[1], bounds[2]];
                    } else if (bounds[2] < 0) {
                        bounds = [bounds[0], bounds[1], 0];
                    }
               }
            } else if (selectedOption == "cloudiness" || selectedOption =="precipitation %") {
                if (scale_type == "absolute"){
                    bounds = [0, 50, 100];
                }
            } else if (selectedOption == "rain" || selectedOption =="snow" || selectedOption =="wind_speed") {
                if (scale_type == "absolute"){
                    bounds = [0, bounds[1], bounds[2]];
                }
            }

            return bounds;
    }

    function addLegend(bounds, colors){
        var legendFullWidth = 1200;
        var legendFullHeight = 50;

        var legendSvg = d3.select('#legend-svg')
        .attr('width', legendFullWidth)
        .attr('height', legendFullHeight)
        .append('g');

        updateColourScale(bounds, colors);

    }

    function getColors(dataType){

            if (dataType == "temp" || dataType == "feels_like"){
                return ["blue", "white", "red"]
            } else if (dataType == "cloudiness"){
                return ["white", "grey", "black"]
             } else if (dataType =="precipitation %") {
                return ["green", "yellow", "red"]
            } else if (dataType == "rain" || dataType =="snow") {
                return ["white", "blue", "purple"]
            } else if(dataType == "wind_speed"){
                return ["yellow", "orange", "red"]
            }
    }

    function updateColourScale(bounds, colors) {


        // clear current legend
        var legendSvg = d3.select('#legend-svg')
        legendSvg.selectAll('*').remove()

        var legendHeight = parseFloat(legendSvg.style('height'))
        var legendWidth = parseFloat(legendSvg.style('width'))
        var barHeight = legendHeight - 20;

        // append gradient bar
        var gradient = legendSvg.append('defs')
            .append('linearGradient')
            .attr('id', 'gradient')
            .attr('x1', '0%') // bottom
            .attr('y1', '0%')
            .attr('x2', '100%') // to top
            .attr('y2', '0%')
            .attr('spreadMethod', 'pad');

        scale_bounds = [0, (bounds[1]-bounds[0])/ (bounds[2]-bounds[0])*100, 100];

        var myColor = d3.scaleLinear().domain(scale_bounds).range(colors);
        // programatically generate the gradient for the legend
        // this creates an array of [pct, colour] pairs as stop
        // values for legend

        var pct = linspace(0, 100, 10).map(function(d) {
            return [Math.round(d) + "%", myColor(d)];
        });

        pct.forEach(function(d) {
            gradient.append('stop')
                .attr('offset', d[0])
                .attr('stop-color', d[1])
                .attr('stop-opacity', 1);
        });

        legendSvg.append('rect')
            .attr('x1', 0)
            .attr('y1', 0)
            .attr('width', legendWidth)//)
            .attr('height',barHeight)//legendSvg['height'])
            .style('fill', 'url(#gradient)');


        // create a scale and axis for the legend

         legend_bounds = [0, ((bounds[1]-bounds[0])/ (bounds[2]-bounds[0])) * legendWidth, legendWidth];

         console.log(legend_bounds);
         console.log(bounds);
        var legendScale = d3.scaleLinear()
            .domain(bounds)
            .range(legend_bounds);

        var legendAxis = d3.axisBottom()
            .scale(legendScale)
            .ticks(d3.min([30,bounds[2]]))
            .tickFormat(d3.format("d"));

        legendSvg.append("g")
            .attr("class", "axis")
            .attr("transform", "translate(0, " + barHeight + ")")
            .call(legendAxis);
    }


        function linspace(start, end, n) {
        var out = [];
        var delta = (end - start) / (n - 1);

        var i = 0;
        while(i < (n - 1)) {
            out.push(start + (i * delta));
            i++;
        }

        out.push(end);
        return out;
    }
