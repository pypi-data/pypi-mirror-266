import React from "react";
import { IoArrowBack } from "react-icons/io5";
import portfolio from "../../../src/images/portfolio.png";

const DocumentSidebar = () => {
  return (
    <>
      <div className="w-full">
        <h1 className="text-[21px] font-cerebri text-[#495057] leading-[27px] my-6 mx-5">
          Report Builder
        </h1>
        <hr />
        <div className="p-5">
          <div className="flex gap-3 items-center">
            <IoArrowBack className="text-[#3C3C3C] text-[20px] font-cerebri leading-[24px]" />
            <h1 className="text-[#3C3C3C] text-[20px] font-cerebri leading-[24px]">
              Portfolios
            </h1>
          </div>
          <div className="mt-10">
            <div>
              <div className="flex items-center gap-3">
                <img src={portfolio} alt="portfolio" />
                <p className="text-[#3C3C3C] text-[16px] font-cerebriregular leading-[24px]">
                  Portfolio 1
                </p>
              </div>
              <div className="mt-5 ms-14 xxl:ms-5">
                <p className="text-[#3C3C3C] text-[16px] font-cerebri leading-[24px]">
                  Holdings
                </p>
                <div className="mt-3 ms-5 xxl:ms-0">
                  <p className="text-[#3C3C3C] text-[16px] font-cerebriregular leading-[24px] bg-customBg px-4 py-3 rounded-xl border border-customBorder w-fit">
                    Portfolio.csv
                  </p>
                  <p className="text-[#3C3C3C] text-[16px] font-cerebriregular leading-[24px] bg-customBg px-4 py-3 rounded-xl border border-customBorder w-fit mt-2">
                    Benchmarck.csv
                  </p>
                </div>
                <p className="text-[#3C3C3C] text-[16px] font-cerebri leading-[24px] mt-5">
                  Risk
                </p>
                <p className="text-[#3C3C3C] text-[16px] font-cerebriregular leading-[24px] bg-customBg px-4 py-3 rounded-xl border border-customBorder w-fit mt-3 ms-5 xxl:ms-0">
                  Risk Report.csv
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3 mt-6">
              <img src={portfolio} alt="portfolio" />
              <p className="text-[#3C3C3C] text-[16px] font-cerebriregular leading-[24px]">
                Portfolio 2
              </p>
            </div>
            <div>
              <div className="flex items-center gap-3 mt-6">
                <img src={portfolio} alt="portfolio" />
                <p className="text-[#3C3C3C] text-[16px] font-cerebriregular leading-[24px]">
                  Portfolio 3
                </p>
              </div>
              <p className="text-[#3C3C3C] text-[16px] font-cerebriregular leading-[24px] bg-customBg px-4 py-3 rounded-xl border border-customBorder w-fit mt-4 ms-20 xxl:ms-5">
                Portfolio.csv
              </p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default DocumentSidebar;
