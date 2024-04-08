import React, { useCallback, useRef, useState } from "react";
import Sidebar from "../components/Sidebar";
import { BiMinus } from "react-icons/bi";
import menuIcon from "../assets/Frame.svg";
import Drawer from "react-modern-drawer";
import close from "../assets/close.svg";
import Header from "../components/Header";
import DocumentSidebar from "../components/document/DocumentSidebar";
import portfolio from "../../src/images/portfolio.png";
import docprofile from "../../src/images/docprofile.png";
import { FiTable } from "react-icons/fi";
import { RiArrowLeftSLine, RiArrowRightSLine } from "react-icons/ri";
import docwave from "../images/docwave.png";
import { time } from "ag-charts-community";
import { AgChartsReact } from "ag-charts-react";
import { BsGraphUp } from "react-icons/bs";
import { MdPieChartOutline } from "react-icons/md";
import { IoMdCard } from "react-icons/io";
import Table from "../components/DocumentBox/Table";
import { IoClose } from "react-icons/io5";

var lastTime = new Date("07 Jan 2020 13:25:00 GMT").getTime();
var data = [];
function getData() {
  data.shift();
  while (data.length < 20) {
    data.push({
      time: new Date((lastTime += 1000)),
      voltage: 1.1 + Math.random() / 2,
    });
  }
  return data;
}

function getData1() {
  return [
    { asset: "Stocks", amount: 60000 },
    { asset: "Bonds", amount: 40000 },
    { asset: "Cash", amount: 7000 },
    { asset: "Real Estate", amount: 5000 },
    { asset: "Commodities", amount: 3000 },
  ];
}

const Document = () => {
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const chartRef = useRef(null);
  const [updating, setUpdating] = useState(false);
  const [showTable, setShowTable] = useState(false);
  const [showGraph, setShowGraph] = useState(false);
  const [showChart, setShowChart] = useState(false);
  const [portfolioCard, setPortfolioCard] = useState(false);
  const [todayCard, setTodayCard] = useState(false);
  const [gainCard, setGainCard] = useState(false);
  const [showCard, setShowCard] = useState(false);
  const [options, setOptions] = useState({
    data: getData(),
    series: [
      {
        xKey: "time",
        yKey: "voltage",
      },
    ],
    axes: [
      {
        type: "time",
        position: "bottom",
        nice: false,
        tick: {
          interval: time.second.every(5),
        },
        label: {
          format: "%H:%M:%S",
        },
      },
      {
        type: "number",
        position: "left",
        label: {
          format: "#{.2f}V",
        },
      },
    ],
    title: {
      text: "Core Voltage",
    },
  });

  const [chartOptions, setChartOptions] = useState({
    data: getData1(),
    title: {
      text: "Portfolio Composition",
    },
    series: [
      {
        type: "pie",
        angleKey: "amount",
        calloutLabelKey: "asset",
        sectorLabelKey: "amount",
        sectorLabel: {
          color: "white",
          fontWeight: "bold",
          formatter: ({ value }) => `$${(value / 1000).toFixed(0)}K`,
        },
      },
    ],
  });

  const update = useCallback(() => {
    const clone = { ...options };

    clone.data = getData();

    setOptions(clone);
  }, [getData, options]);

  const startUpdates = useCallback(() => {
    if (updating) {
      return;
    }
    setUpdating(true);
    update();
    setInterval(update, 500);
  }, [updating]);

  const toggleDrawer = () => {
    setIsDrawerOpen(!isDrawerOpen);
  };

  const [isDragging, setIsDragging] = useState(false);

  const handleDragStart = (event) => {
    event.dataTransfer.setData("text/plain", event.target.id);
    setIsDragging(true);
  };

  const handleDragEnd = () => {
    setIsDragging(false);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    const draggableId = event.dataTransfer.getData("text/plain");
    const draggedElement = document.getElementById(draggableId);
    const dropTarget = event.currentTarget;

    if (dropTarget === event.target || dropTarget.contains(event.target)) {
      const titleElement = document.getElementById("table");
      const titleElement1 = document.getElementById("graph");
      const titleElement2 = document.getElementById("chart");
      const titleElement3 = document.getElementById("card");
      const titleElement4 = document.getElementById("todayCard");
      const titleElement5 = document.getElementById("gainCard");
      const titleElement6 = document.getElementById("portfolioCard");

      if (titleElement && draggableId == "drag-source3") {
        titleElement.remove();
        setShowTable(true);
      }
      if (titleElement1 && draggableId === "drag-source4") {
        titleElement1.remove();
        setShowGraph(true);
      }
      if (titleElement2 && draggableId === "drag-source5") {
        titleElement2.remove();
        setShowChart(true);
      }
      if (titleElement3 && draggableId === "drag-source6") {
        titleElement3.remove();
        setShowCard(true);
      }
      if (titleElement4 && draggableId === "drag-source9") {
        titleElement4.remove();
        setTodayCard(true);
      }
      if (titleElement5 && draggableId === "drag-source8") {
        titleElement5.remove();
        setGainCard(true);
      }
      if (titleElement6 && draggableId === "drag-source7") {
        titleElement6.remove();
        setPortfolioCard(true);
      }

      dropTarget.insertBefore(draggedElement, dropTarget.firstChild);

      // dropTarget.appendChild(draggedElement);
    }

    setIsDragging(false);
  };

  // const handleDrop = (event) => {
  //     event.preventDefault();
  //     const draggableId = event.dataTransfer.getData("text/plain");
  //     const draggedElement = document.getElementById(draggableId);
  //     const dropTarget = event.currentTarget;

  //     if (dropTarget === event.target || dropTarget.contains(event.target)) {
  //         const titleElement = document.getElementById("table");
  //         if (titleElement) {
  //             titleElement.remove();
  //         }

  //         // dropTarget.insertBefore(draggedElement, dropTarget.firstChild);

  //         dropTarget.appendChild(draggedElement);
  //         setShowTable(true);
  //     }

  //     setIsDragging(false);
  // };

  const handleDragOver = (event) => {
    event.preventDefault();
  };

  return (
    <>
      <div className="flex lg:block">
        <div className="z-[999]">
          <img
            src={menuIcon}
            className={`hidden xl:flex xl:absolute w-[27px] h-[27px] mx-4 my-8 ${
              isDrawerOpen === true ? "xl:hidden" : ""
            }`}
            onClick={toggleDrawer}
            alt=""
          />
        </div>

        <div className="xl:hidden w-1/5 font-cerebri flex border-r-[0.5px] border-[#CDCDCD]">
          <Sidebar />
          <DocumentSidebar />
        </div>

        <Drawer
          open={isDrawerOpen}
          onClose={toggleDrawer}
          direction="left"
          className="chatDrawer"
        >
          <Sidebar />
          <div className="font-cerebri w-[-webkit-fill-available] flex flex-col justify-between">
            <img
              src={close}
              className="w-[14px] h-[14px] absolute right-3 top-5"
              onClick={toggleDrawer}
              alt=""
            />
            <DocumentSidebar />
          </div>
        </Drawer>

        <div className="w-full">
          <Header />
          <div className="flex lg:flex-col">
            <div className="w-4/5 bg-[#f3f4f6] lg:w-full">
              <div className="px-4 py-2">
                <div className="bg-[#fff] rounded-xl px-5 py-5 mt-4 h-[calc(100vh-205px)] overflow-auto scrollbar">
                  <div className="flex justify-between gap-7 xxl:flex-wrap pb-4">
                    <div
                      className="w-full xxl:w-[200px] xs:w-full"
                      id="drop-target7"
                      onDrop={handleDrop}
                      onDragOver={handleDragOver}
                    >
                      <div className="rounded-md shadow-dropCard px-5 pt-4 pb-2 w-full xxl:w-[200px] xs:w-full xs:text-center">
                        <p className="text-[#808080] text-[16px] font-cerebrisemibold leading-[24px]">
                          Your Portfolio Value
                        </p>
                        <h1 className="text-[#000000] text-[20px] font-cerebrisemibold leading-[40px]">
                          $5,078,89
                        </h1>
                      </div>
                    </div>
                    <div
                      className="w-full xxl:w-[200px] xs:w-full"
                      id="drop-target8"
                      onDrop={handleDrop}
                      onDragOver={handleDragOver}
                    >
                      <div className="rounded-md shadow-dropCard px-5 pt-4 pb-2 w-full  xxl:w-[200px] xs:w-full xs:text-center">
                        <p className="text-[#808080] text-[16px] font-cerebrisemibold leading-[24px]">
                          Today’s Gain
                        </p>
                        <h1 className="text-[#000000] text-[20px] font-cerebrisemibold leading-[40px]">
                          +85,87 (1,35%)
                        </h1>
                      </div>
                    </div>
                    <div
                      className="w-full xxl:w-[200px] xs:w-full"
                      id="drop-target9"
                      onDrop={handleDrop}
                      onDragOver={handleDragOver}
                    >
                      <div className="rounded-md shadow-dropCard px-5 pt-4 pb-2 w-full  xxl:w-[200px] xs:w-full xs:text-center">
                        <p className="text-[#808080] text-[16px] font-cerebrisemibold leading-[24px]">
                          Today’s Gain
                        </p>
                        <h1 className="text-[#000000] text-[20px] font-cerebrisemibold leading-[40px]">
                          +843,70 (7,35%)
                        </h1>
                      </div>
                    </div>
                    <div
                      className="w-full xxl:w-[200px] xs:w-full"
                      id="drop-target6"
                      onDrop={handleDrop}
                      onDragOver={handleDragOver}
                    >
                      <div className="rounded-md shadow-dropCard px-5 pt-4 pb-2 w-full  xxl:w-[200px] xs:w-full xs:text-center">
                        <p className="text-[#808080] text-[16px] font-cerebrisemibold leading-[24px]">
                          Today’s Gain
                        </p>
                        <h1 className="text-[#000000] text-[20px] font-cerebrisemibold leading-[40px]">
                          +844,70 (7,35%)
                        </h1>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-rows-1">
                    <div className="grid grid-cols-12 my-4 space-x-5 space-y-5">
                      <div
                        className="col-span-6 xl:col-span-12"
                        id="drop-target1"
                        onDrop={handleDrop}
                        onDragOver={handleDragOver}
                      >
                        <div
                          className="wrapper h-[384px]"
                          id="drag-source12"
                          draggable
                          onDragStart={handleDragStart}
                          onDragEnd={handleDragEnd}
                        >
                          <AgChartsReact ref={chartRef} options={options} />
                        </div>
                      </div>

                      <div
                        className="xxl:mt-4 col-span-6 xl:col-span-12"
                        id="drop-target2"
                        onDrop={handleDrop}
                        onDragOver={handleDragOver}
                      >
                        <div
                          className="h-[384px]"
                          id="drag-source13"
                          draggable
                          onDragStart={handleDragStart}
                          onDragEnd={handleDragEnd}
                        >
                          <AgChartsReact options={chartOptions} />
                        </div>
                      </div>

                      <div
                        className="col-span-6 xl:col-span-12"
                        id="drop-target3"
                        onDrop={handleDrop}
                        onDragOver={handleDragOver}
                      >
                        <div
                          id="drag-source11"
                          draggable
                          onDragStart={handleDragStart}
                          onDragEnd={handleDragEnd}
                        >
                          <Table />
                        </div>
                      </div>

                      <div
                        className="col-span-6 xl:col-span-12"
                        id="drop-target4"
                        onDrop={handleDrop}
                        onDragOver={handleDragOver}
                      >
                        <div className="flex items-center justify-between">
                          <h1 className="text-[#000000] text-[20px] font-cerebri leading-[32px]">
                            Indices
                          </h1>
                          <div className="flex items-center gap-3">
                            <RiArrowLeftSLine className="text-[23px]" />
                            <RiArrowRightSLine className="text-[23px]" />
                          </div>
                        </div>
                        <div className="cursor-pointer">
                          <table className="bg-white w-full">
                            <thead>
                              <tr>
                                <th className="px-3 py-3 border-b-2 border-gray-300 text-left text-xs font-cerebriregular leading-[20px] text-[#808080] uppercase">
                                  Company
                                </th>
                                <th className="px-3 py-3 border-b-2 border-gray-300 text-left text-xs font-cerebriregular leading-[20px] text-[#808080] uppercase">
                                  Last Price
                                </th>
                                <th className="px-3 py-3 border-b-2 border-gray-300 text-left text-xs font-cerebriregular leading-[20px] text-[#808080] uppercase">
                                  Change
                                </th>
                                <th className="px-3 py-3 border-b-2 border-gray-300 text-left text-xs font-cerebriregular leading-[20px] text-[#808080] uppercase">
                                  7-Day Chart
                                </th>
                              </tr>
                            </thead>
                            <tbody className="bg-white">
                              <tr>
                                <td className="p-2 text-[14px] leading-[20px] font-cerebribold text-[#000000] border-b border-gray-200">
                                  S&P/TSX
                                </td>
                                <td className="p-2 text-[14px] leading-[20px] font-cerebribold text-[#000000] border-b border-gray-200">
                                  $19,626.34
                                </td>
                                <td className="p-2 text-[14px] leading-[20px] text-[#000000] border-b border-gray-200">
                                  <p className="font-cerebribold text-customColor">
                                    +547.34
                                  </p>
                                  <p className="font-cerebriregular">+2.87%</p>
                                </td>
                                <td>
                                  <img src={docwave} alt="docwave" />
                                </td>
                              </tr>
                              <tr>
                                <td className="p-2 text-[14px] leading-[20px] font-cerebribold text-[#000000] border-b border-gray-200">
                                  S&P 500
                                </td>
                                <td className="p-2 text-[14px] leading-[20px] font-cerebribold text-[#000000] border-b border-gray-200">
                                  $4,626.34
                                </td>
                                <td className="p-2 text-[14px] leading-[20px] text-[#000000] border-b border-gray-200">
                                  <p className="font-cerebribold text-customColor">
                                    +79.34
                                  </p>
                                  <p className="font-cerebriregular">+1.87%</p>
                                </td>
                                <td>
                                  <img src={docwave} alt="docwave" />
                                </td>
                              </tr>
                              <tr>
                                <td className="p-2 text-[14px] leading-[20px] font-cerebribold text-[#000000] border-b border-gray-200">
                                  DOW
                                </td>
                                <td className="p-2 text-[14px] leading-[20px] font-cerebribold text-[#000000] border-b border-gray-200">
                                  $19,626.34
                                </td>
                                <td className="p-2 text-[14px] leading-[20px] text-[#000000] border-b border-gray-200">
                                  <p className="font-cerebribold text-customColor">
                                    +547.34
                                  </p>
                                  <p className="font-cerebriregular">+2.87%</p>
                                </td>
                                <td>
                                  <img src={docwave} alt="docwave" />
                                </td>
                              </tr>
                              <tr>
                                <td className="p-2 text-[14px] leading-[20px] font-cerebribold text-[#000000] border-b border-gray-200">
                                  CAD/USD
                                </td>
                                <td className="p-2 text-[14px] leading-[20px] font-cerebribold text-[#000000] border-b border-gray-200">
                                  $0,7278
                                </td>
                                <td className="p-2 text-[14px] leading-[20px] text-[#000000] border-b border-gray-200">
                                  <p className="font-cerebribold text-customColor">
                                    +0.0034
                                  </p>
                                  <p className="font-cerebriregular">+2.87%</p>
                                </td>
                                <td>
                                  <img src={docwave} alt="docwave" />
                                </td>
                              </tr>
                              <tr>
                                <td className="p-2 text-[14px] leading-[20px] font-cerebribold text-[#000000] border-b border-gray-200">
                                  Bitcoin CAD
                                </td>
                                <td className="p-2 text-[14px] leading-[20px] font-cerebribold text-[#000000] border-b border-gray-200">
                                  $82.73
                                </td>
                                <td className="p-2 text-[14px] leading-[20px] text-[#000000] border-b border-gray-200">
                                  <p className="font-cerebribold text-customColor">
                                    +82.34
                                  </p>
                                  <p className="font-cerebriregular">+0.27%</p>
                                </td>
                                <td>
                                  <img src={docwave} alt="docwave" />
                                </td>
                              </tr>
                              <tr>
                                <td className="p-2 text-[14px] leading-[20px] font-cerebribold text-[#000000]">
                                  NACDAQ
                                </td>
                                <td className="p-2 text-[14px] leading-[20px] font-cerebribold text-[#000000]">
                                  $82.73
                                </td>
                                <td className="p-2 text-[14px] leading-[20px] text-[#000000]">
                                  <p className="font-cerebribold text-customColor">
                                    +82.34
                                  </p>
                                  <p className="font-cerebriregular">+0.27%</p>
                                </td>
                                <td>
                                  <img src={docwave} alt="docwave" />
                                </td>
                              </tr>
                            </tbody>
                          </table>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="bg-customBg border rounded-md px-12 py-2 flex items-center justify-between mt-4">
                  <h1 className="text-[#3C3C3C] text-[14px] font-cerebriregular leading-[24px]">
                    Audience
                  </h1>
                  <div className="flex items-center gap-2">
                    <img src={docprofile} alt="docprofile" />
                    <h1 className="text-[#3C3C3C] text-[14px] font-cerebriregular leading-[24px]">
                      Risk Model Agent
                    </h1>
                  </div>
                  <div className="flex items-center gap-2">
                    <img src={docprofile} alt="docprofile" />
                    <h1 className="text-[#3C3C3C] text-[14px] font-cerebriregular leading-[24px]">
                      vs Benchmark Agent
                    </h1>
                  </div>
                  <h1 className="text-[#3C3C3C] text-[14px] font-cerebriregular leading-[24px]">
                    Agent 3
                  </h1>
                </div>
              </div>
            </div>
            <div className="w-1/5 h-[calc(100vh-93px)] overflow-auto scrollbar border-l-[0.5px] border-[#CDCDCD] px-5 py-6  lg:w-full lg:h-auto">
              <h1 className="text-[#3C3C3C] text-[20px] font-cerebri leading-[24px]">
                Outputs
              </h1>

              <div
                id="drop-target"
                onDrop={handleDrop}
                onDragOver={handleDragOver}
              >
                <div
                  className="flex gap-3 items-center cursor-pointer"
                  id="drag-source7"
                  draggable
                  onDragStart={handleDragStart}
                  onDragEnd={handleDragEnd}
                >
                  <div className="flex gap-3 mt-5" id="portfolioCard">
                    <div className="bg-customBg p-3 rounded-xl border border-customBorder w-fit">
                      <IoMdCard />
                    </div>
                    <p className="text-[#3C3C3C] mt-2 text-[16px] font-cerebriregular leading-[24px]">
                      Portfolio Card
                    </p>
                  </div>

                  {portfolioCard && (
                    <div
                      className="w-full cursor-pointer mb-4 relative"
                      // id="drop-target7"
                      // onDrop={handleDrop}
                      // onDragOver={handleDragOver}
                    >
                      <div>
                        <div className="rounded-md shadow-dropCard px-5 pt-4 pb-2 w-full xxl:w-[200px] xs:w-full xs:text-center">
                          <p className="text-[#808080] text-[16px] font-cerebrisemibold leading-[24px]">
                            Your Portfolio Value
                          </p>
                          <h1 className="text-[#000000] text-[20px] font-cerebrisemibold leading-[40px]">
                            $5,078,89
                          </h1>
                        </div>
                      </div>
                      {/* <IoClose className="absolute top-2 right-2" /> */}
                    </div>
                  )}
                </div>

                <div
                  className="flex gap-3 items-center cursor-pointer"
                  id="drag-source9"
                  draggable
                  onDragStart={handleDragStart}
                  onDragEnd={handleDragEnd}
                >
                  <div className="flex gap-3 mt-5" id="todayCard">
                    <div className="bg-customBg p-3 rounded-xl border border-customBorder w-fit">
                      <IoMdCard />
                    </div>
                    <p className=" text-[#3C3C3C] mt-2 text-[16px] font-cerebriregular leading-[24px]">
                      Today’s Card
                    </p>
                  </div>

                  {todayCard && (
                    <div
                      id="drop-target8"
                      onDrop={handleDrop}
                      onDragOver={handleDragOver}
                      className="mb-4 rounded-md shadow-dropCard px-5 pt-4 pb-2 w-full  xxl:w-[200px] xs:w-full xs:text-center"
                    >
                      <p className="text-[#808080] text-[16px] font-cerebrisemibold leading-[24px]">
                        Today’s Gain
                      </p>
                      <h1 className="text-[#000000] text-[20px] font-cerebrisemibold leading-[40px]">
                        +85,87 (1,35%)
                      </h1>
                    </div>
                  )}
                </div>
                <div
                  className="flex gap-3 items-center cursor-pointer"
                  id="drag-source8"
                  draggable
                  onDragStart={handleDragStart}
                  onDragEnd={handleDragEnd}
                >
                  <div className="flex gap-3 mt-5" id="gainCard">
                    <div className="bg-customBg p-3 rounded-xl border border-customBorder w-fit">
                      <IoMdCard />
                    </div>
                    <p className=" text-[#3C3C3C] mt-2 text-[16px] font-cerebriregular leading-[24px]">
                      Gain Card
                    </p>
                  </div>

                  {gainCard && (
                    <div
                      id="drop-target9"
                      onDrop={handleDrop}
                      onDragOver={handleDragOver}
                      className="mb-4 rounded-md shadow-dropCard px-5 pt-4 pb-2 w-full  xxl:w-[200px] xs:w-full xs:text-center"
                    >
                      <p className="text-[#808080] text-[16px] font-cerebrisemibold leading-[24px]">
                        Today’s Gain
                      </p>
                      <h1 className="text-[#000000] text-[20px] font-cerebrisemibold leading-[40px]">
                        +843,70 (7,35%)
                      </h1>
                    </div>
                  )}
                </div>
                <div
                  className="flex gap-3 items-center cursor-pointer"
                  id="drag-source6"
                  draggable
                  onDragStart={handleDragStart}
                  onDragEnd={handleDragEnd}
                >
                  <div className="flex gap-3 mt-5" id="card">
                    <div className="bg-customBg p-3 rounded-xl border border-customBorder w-fit">
                      <IoMdCard />
                    </div>
                    <p className=" text-[#3C3C3C] mt-2 text-[16px] font-cerebriregular leading-[24px]">
                      Card
                    </p>
                  </div>

                  {showCard && (
                    <div
                      id="drop-target6"
                      onDrop={handleDrop}
                      onDragOver={handleDragOver}
                      className="mb-4 rounded-md shadow-dropCard px-5 pt-4 pb-2 w-full  xxl:w-[200px] xs:w-full xs:text-center"
                    >
                      <p className="text-[#808080] text-[16px] font-cerebrisemibold leading-[24px]">
                        Today’s Gain
                      </p>
                      <h1 className="text-[#000000] text-[20px] font-cerebrisemibold leading-[30px]">
                        +844,70 (7,35%)
                      </h1>
                    </div>
                  )}
                </div>

                <div
                  className="flex gap-3 mt-5 items-center cursor-pointer"
                  id="drag-source3"
                  draggable
                  onDragStart={handleDragStart}
                  onDragEnd={handleDragEnd}
                >
                  <div className="flex gap-3" id="table">
                    <div className="bg-customBg p-3 rounded-xl border border-customBorder w-fit">
                      <FiTable />
                    </div>
                    <p className=" text-[#3C3C3C] mt-2 text-[16px] font-cerebriregular leading-[24px]">
                      Table
                    </p>
                  </div>

                  {showTable && (
                    <div className="overflow-x-auto cursor-pointer w-full">
                      <div
                        className="col-span-6 xl:col-span-12"
                        id="drop-target3"
                        onDrop={handleDrop}
                        onDragOver={handleDragOver}
                      >
                        <Table />
                      </div>
                    </div>
                  )}
                </div>

                <div
                  className="flex gap-3 mt-5 items-center cursor-pointer"
                  id="drag-source4"
                  draggable
                  onDragStart={handleDragStart}
                  onDragEnd={handleDragEnd}
                >
                  <div className="flex gap-3" id="graph">
                    <div className="bg-customBg p-3 rounded-xl border border-customBorder w-fit">
                      <BsGraphUp />
                    </div>
                    <p className=" text-[#3C3C3C] mt-2 text-[16px] font-cerebriregular leading-[24px]">
                      Graph
                    </p>
                  </div>

                  {showGraph && (
                    <div className="w-full">
                      <AgChartsReact ref={chartRef} options={options} />
                    </div>
                  )}
                </div>

                <div
                  className="flex gap-3 mt-5 items-center cursor-pointer"
                  id="drag-source5"
                  draggable
                  onDragStart={handleDragStart}
                  onDragEnd={handleDragEnd}
                >
                  <div className="flex gap-3" id="chart">
                    <div className="bg-customBg p-3 rounded-xl border border-customBorder w-fit">
                      <MdPieChartOutline />
                    </div>
                    <p className=" text-[#3C3C3C] mt-2 text-[16px] font-cerebriregular leading-[24px]">
                      Chart
                    </p>
                  </div>

                  {showChart && (
                    <div className="w-full">
                      <AgChartsReact options={chartOptions} />
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Document;
