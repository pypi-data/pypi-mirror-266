import React from "react";
import { RiArrowLeftSLine, RiArrowRightSLine } from "react-icons/ri";
import docwave from "../../images/docwave.png";

const Table = () => {
  return (
    <div>
      <div className="flex items-center justify-between">
        <h1 className="text-[#000000] text-[20px] font-cerebri leading-[32px]">
          Your watchlist
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
                Dow Jones
              </td>
              <td className="p-2 text-[14px] leading-[20px] font-cerebribold text-[#000000] border-b border-gray-200">
                $19,626.34
              </td>
              <td className="p-2 text-[14px] leading-[20px] text-[#000000] border-b border-gray-200">
                <p className="font-cerebribold text-customColor">+547.34</p>
                <p className="font-cerebriregular">+2.87%</p>
              </td>
              <td>
                <img src={docwave} alt="docwave" />
              </td>
            </tr>
            <tr>
              <td className="p-2 text-[14px] leading-[20px] font-cerebribold text-[#000000] border-b border-gray-200">
                Apple
              </td>
              <td className="p-2 text-[14px] leading-[20px] font-cerebribold text-[#000000] border-b border-gray-200">
                $4,626.34
              </td>
              <td className="p-2 text-[14px] leading-[20px] text-[#000000] border-b border-gray-200">
                <p className="font-cerebribold text-customColor">+79.34</p>
                <p className="font-cerebriregular">+1.87%</p>
              </td>
              <td>
                <img src={docwave} alt="docwave" />
              </td>
            </tr>
            <tr>
              <td className="p-2 text-[14px] leading-[20px] font-cerebribold text-[#000000] border-b border-gray-200">
                BTC/USD
              </td>
              <td className="p-2 text-[14px] leading-[20px] font-cerebribold text-[#000000] border-b border-gray-200">
                $19,626.34
              </td>
              <td className="p-2 text-[14px] leading-[20px] text-[#000000] border-b border-gray-200">
                <p className="font-cerebribold text-customColor">+547.34</p>
                <p className="font-cerebriregular">+2.87%</p>
              </td>
              <td>
                <img src={docwave} alt="docwave" />
              </td>
            </tr>
            <tr>
              <td className="p-2 text-[14px] leading-[20px] font-cerebribold text-[#000000] border-b border-gray-200">
                ETH/USD
              </td>
              <td className="p-2 text-[14px] leading-[20px] font-cerebribold text-[#000000] border-b border-gray-200">
                $0,7278
              </td>
              <td className="p-2 text-[14px] leading-[20px] text-[#000000] border-b border-gray-200">
                <p className="font-cerebribold text-customColor">+0.0034</p>
                <p className="font-cerebriregular">+2.87%</p>
              </td>
              <td>
                <img src={docwave} alt="docwave" />
              </td>
            </tr>
            <tr>
              <td className="p-2 text-[14px] leading-[20px] font-cerebribold text-[#000000] border-b border-gray-200">
                EUR/USD
              </td>
              <td className="p-2 text-[14px] leading-[20px] font-cerebribold text-[#000000] border-b border-gray-200">
                $82.73
              </td>
              <td className="p-2 text-[14px] leading-[20px] text-[#000000] border-b border-gray-200">
                <p className="font-cerebribold text-customColor">+82.34</p>
                <p className="font-cerebriregular">+0.27%</p>
              </td>
              <td>
                <img src={docwave} alt="docwave" />
              </td>
            </tr>
            <tr>
              <td className="p-2 text-[14px] leading-[20px] font-cerebribold text-[#000000]">
                EUR/USD
              </td>
              <td className="p-2 text-[14px] leading-[20px] font-cerebribold text-[#000000]">
                $82.73
              </td>
              <td className="p-2 text-[14px] leading-[20px] text-[#000000]">
                <p className="font-cerebribold text-customColor">+82.34</p>
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
  );
};

export default Table;
