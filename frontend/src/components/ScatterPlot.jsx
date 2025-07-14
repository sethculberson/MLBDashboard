import React, { useRef, useEffect } from 'react';
import * as d3 from 'd3';

// Note: Used Google Gemini to assist with this component. Wrote initial structure then refined the UI using the AI's suggestions.

const ScatterPlot = ({
  data, // Array of { player_id, player_name, [statisticKey]: value, ... } for all players in the season
  statisticKey,
  statisticLabel, // for axis label and tooltips
  selectedPlayerId, 
  chartTitle,
  xAxisLabel = 'Players (Sorted by Value)' 
}) => {
  const svgReference = useRef(); 

  useEffect(() => {
    // Check if data is available and not empty
    if (!data || data.length === 0 || !statisticKey) {
      d3.select(svgReference.current).selectAll('*').remove();
      return;
    }

    // Filter out data points where the statisticKey value is null or undefined
    const validData = data.filter(d => d[statisticKey] !== null && d[statisticKey] !== undefined);

    if (validData.length === 0) {
      d3.select(svgReference.current).selectAll('*').remove();
      return;
    }

    // Copy the data and sort it by statisticKey
    const sortedData = [...validData].sort((a, b) => (a[statisticKey] || 0) - (b[statisticKey] || 0));

    const margin = { top: 40, right: 30, bottom: 80, left: 70 }; // Increased bottom margin for player names
    const width = 800 - margin.left - margin.right;
    const height = 500 - margin.top - margin.bottom;

    const svg = d3.select(svgReference.current)
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom);

    svg.selectAll('*').remove(); // Clear previous chart elements

    // Append a group element to apply margins
    const g = svg.append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // --- Scales ---
    // X scale: Ordinal scale for player names (or their index after sorting)
    const xScale = d3.scaleBand()
      .domain(sortedData.map((d, i) => i)) // Use index as domain for x-axis to ensure unique positions
      .range([0, width])
      .padding(0.1); // Padding between bands

    // Y scale: Linear scale for the statistic value
    const yScale = d3.scaleLinear()
      .domain([
        d3.min(sortedData, d => d[statisticKey]) * 0.9, // Start slightly below min value
        d3.max(sortedData, d => d[statisticKey]) * 1.1  // End slightly above max value
      ])
      .range([height, 0]); // Map values to SVG coordinates (top is 0, bottom is height)

    // --- Axes ---
    // X-axis (bottom) - Removed player names from tick labels
    g.append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(xScale)
        .tickFormat("") // Set tickFormat to an empty string to hide labels
      );

    // Y-axis (left)
    g.append("g")
      .call(d3.axisLeft(yScale));

    // --- Labels and Title ---
    // Y-axis label
    g.append("text")
      .attr("transform", "rotate(-90)") // Rotate text for vertical alignment
      .attr("y", 0 - margin.left + 20) // Position to the left of the y-axis
      .attr("x", 0 - (height / 2)) // Center vertically
      .attr("dy", "1em") // Adjust vertical position
      .style("text-anchor", "middle") // Center text horizontally
      .style("font-size", "14px")
      .style("font-weight", "bold")
      .text(statisticLabel);

    // X-axis label (optional, if needed beyond player names)
    g.append("text")
      .attr("x", width / 2)
      .attr("y", height + margin.bottom - 10) // Position below x-axis
      .attr("text-anchor", "middle")
      .style("font-size", "14px")
      .style("font-weight", "bold")
      .text(xAxisLabel);

    // Chart Title
    g.append("text")
      .attr("x", (width / 2))
      .attr("y", 0 - (margin.top / 2)) // Position above the chart area
      .attr("text-anchor", "middle")
      .style("font-size", "18px")
      .style("font-weight", "bold")
      .text(chartTitle);

    // --- Draw Circles (Data Points) ---
    g.selectAll(".dot")
      .data(sortedData) // Bind sorted data to circles
      .enter().append("circle") // Create a circle for each data point
      .attr("class", "dot")
      .attr("cx", (d, i) => xScale(i) + xScale.bandwidth() / 2) // X position: center in its band
      .attr("cy", d => yScale(d[statisticKey] || 0)) // Y position: based on statistic value
      .attr("r", d => d.player_id === selectedPlayerId ? 8 : 5) // Larger radius for highlighted player
      .style("fill", d => d.player_id === selectedPlayerId ? "#ff4500" : "#4682b4") // Orange-red for highlighted, steelblue for others
      .style("stroke", d => d.player_id === selectedPlayerId ? "black" : "none") // Black stroke for highlighted
      .style("stroke-width", d => d.player_id === selectedPlayerId ? 2 : 0) // Thicker stroke for highlighted
      .append("title") // Add a tooltip on hover
      .text(d => `${d.player_name}: ${statisticLabel} = ${d[statisticKey] ? d[statisticKey] : 'N/A'}`); // Format tooltip text

  }, [data, statisticKey, statisticLabel, selectedPlayerId, chartTitle, xAxisLabel]); // Redraw when these props change

  return (
    <div className="scatterplot-container">
      <svg ref={svgReference}></svg> {/* SVG element where D3 will draw */}
    </div>
  );
};

export default ScatterPlot;