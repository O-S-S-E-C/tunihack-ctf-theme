import { mergeObjects } from "../../objects";
import { cumulativeSum } from "../../math";
import dayjs from "dayjs";

const graphColors = ["#22d3ee", "#60a5fa", "#38bdf8", "#34d399", "#fbbf24"];

export function getOption(mode, places, optionMerge) {
  let option = {
    backgroundColor: "transparent",
    textStyle: { color: "#a5b3d1" },
    title: {
      left: "center",
      text: "Top 10 " + (mode === "teams" ? "Teams" : "Users"),
      textStyle: { color: "#e8eefc", fontWeight: 600 },
    },
    tooltip: {
      trigger: "axis",
      axisPointer: {
        type: "cross",
      },
    },
    legend: {
      type: "scroll",
      orient: "horizontal",
      align: "left",
      bottom: 35,
      data: [],
      textStyle: { color: "#b8c7e2" },
    },
    toolbox: {
      feature: {
        dataZoom: {
          yAxisIndex: "none",
        },
        saveAsImage: {},
      },
    },
    grid: {
      containLabel: true,
    },
    xAxis: [
      {
        type: "time",
        boundaryGap: false,
        data: [],
        axisLabel: { color: "#a5b3d1" },
        axisLine: { lineStyle: { color: "rgba(96,165,250,.25)" } },
        splitLine: { lineStyle: { color: "rgba(96,165,250,.10)" } },
      },
    ],
    yAxis: [
      {
        type: "value",
        axisLabel: { color: "#a5b3d1" },
        axisLine: { lineStyle: { color: "rgba(96,165,250,.25)" } },
        splitLine: { lineStyle: { color: "rgba(96,165,250,.12)" } },
      },
    ],
    dataZoom: [
      {
        id: "dataZoomX",
        type: "slider",
        xAxisIndex: [0],
        filterMode: "filter",
        height: 20,
        top: 35,
        fillerColor: "rgba(34, 211, 238, 0.14)",
      },
    ],
    series: [],
  };

  const teams = Object.keys(places);
  for (let i = 0; i < teams.length; i++) {
    const team_score = [];
    const times = [];
    for (let j = 0; j < places[teams[i]]["solves"].length; j++) {
      team_score.push(places[teams[i]]["solves"][j].value);
      const date = dayjs(places[teams[i]]["solves"][j].date);
      times.push(date.toDate());
    }

    const total_scores = cumulativeSum(team_score);
    let scores = times.map(function (e, i) {
      return [e, total_scores[i]];
    });

    option.legend.data.push(places[teams[i]]["name"]);

    const data = {
      name: places[teams[i]]["name"],
      type: "line",
      label: {
        normal: {
          position: "top",
        },
      },
      itemStyle: {
        normal: {
          color: graphColors[i % graphColors.length],
        },
      },
      data: scores,
    };
    option.series.push(data);
  }

  if (optionMerge) {
    option = mergeObjects(option, optionMerge);
  }
  return option;
}
