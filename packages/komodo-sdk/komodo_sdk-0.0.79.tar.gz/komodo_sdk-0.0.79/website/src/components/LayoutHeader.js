import React, { useContext, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import homemenu from "../../src/images/homemenu.png";
import close from "../../src/assets/close.svg";
import Drawer from "react-modern-drawer";
import { RiCloseFill } from "react-icons/ri";
import { SlSocialLinkedin } from "react-icons/sl";
import roleContext from "../contexts/roleContext";

const LayoutHeader = () => {
  const komodoUser = JSON.parse(localStorage.getItem("komodoUser"));
  const location = useLocation();
  const selectContext = useContext(roleContext);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  const toggleDrawer = () => {
    setIsDrawerOpen(!isDrawerOpen);
  };

  return (
    <>
      <div className="flex items-center w-full justify-between py-7 lg:px-6">
        <h1 className="text-3xl font-cerebrisemibold ">
          {selectContext?.company}
        </h1>
        <div className="flex gap-14 lg:hidden">
          <Link to="/home">
            <p
              className={`text-[20px] font-cerebriregular leading-[24px] ${
                location?.pathname === "/home"
                  ? "text-[#316FF6]"
                  : "text-[#333333]"
              }`}
            >
              Home
            </p>
          </Link>
          <Link to="/pricing">
            <p
              className={`text-[20px] font-cerebriregular leading-[24px] ${
                location?.pathname === "/pricing"
                  ? "text-[#316FF6]"
                  : "text-[#333333]"
              }`}
            >
              Pricing
            </p>
          </Link>
        </div>
        <div className="flex gap-6 lg:justify-end lg:gap-3 lg:hidden">
          <div className="flex gap-3">
            {komodoUser?.email !== null &&
            komodoUser?.email !== undefined &&
            komodoUser?.email !== "" ? null : (
              <>
                <Link to="/login">
                  <button className="bg-[#F3F7FF] text-[18px] font-cerebri border text-customBlue border-[#C7D8FD] py-2 px-4 rounded-[10px] min-w-[107px]">
                    Login
                  </button>
                </Link>
                <Link to="/signup">
                  <button className="bg-customBlue text-[18px]  font-cerebri py-2 px-5 text-white rounded-[10px] min-w-[113px]">
                    Sign up
                  </button>
                </Link>
              </>
            )}

            <Link to="/chat">
              <button className="bg-customBlue text-[18px] font-cerebri py-2 px-5 text-white rounded-[10px] min-w-[113px]">
                Try Now
              </button>
            </Link>
          </div>
        </div>

        <img
          src={homemenu}
          alt="homemenu"
          className="bg-customBlue p-4 rounded-[10px] hidden cursor-pointer lg:block"
          onClick={toggleDrawer}
        />
      </div>

      <Drawer
        open={isDrawerOpen}
        onClose={toggleDrawer}
        direction="left"
        className="chatDrawer"
      >
        <div className="font-cerebri w-full">
          {/* <img
            src={close}
            className="w-[14px] h-[14px] absolute right-3 top-5"
            onClick={toggleDrawer}
            alt=""
          /> */}
          <div
            className="bg-customBlue p-2 rounded-full w-fit  absolute right-3 top-5"
            onClick={toggleDrawer}
          >
            <RiCloseFill className="text-[23px] text-[#fff]" />
          </div>
          <div className="p-5 mt-3">
            <Link to="/home">
              <p
                className={`text-[20px] font-cerebriregular leading-[24px] mb-5 ${
                  location?.pathname === "/home"
                    ? "text-[#316FF6]"
                    : "text-[#333333]"
                }`}
              >
                Home
              </p>
            </Link>
            <Link to="/pricing">
              <p
                className={`text-[20px] font-cerebriregular leading-[24px] mb-5 ${
                  location?.pathname === "/pricing"
                    ? "text-[#316FF6]"
                    : "text-[#333333]"
                }`}
              >
                Pricing
              </p>
            </Link>
            <hr />
            <div className="mt-5">
              {komodoUser?.email !== null &&
              komodoUser?.email !== undefined &&
              komodoUser?.email !== "" ? null : (
                <>
                  <Link to="/login">
                    <button className="bg-[#F3F7FF] text-[18px] font-cerebri border text-customBlue border-[#C7D8FD] py-2 px-4 rounded-[10px] w-full">
                      Login
                    </button>
                  </Link>
                  <Link to="/signup">
                    <button className="bg-customBlue text-[18px]  font-cerebri py-2 px-5 text-white rounded-[10px] w-full my-5">
                      Sign up
                    </button>
                  </Link>
                </>
              )}

              <Link to="/chat">
                <button className="bg-customBlue text-[18px] font-cerebri py-2 px-5 text-white rounded-[10px] w-full">
                  Try Now
                </button>
              </Link>
            </div>
          </div>
        </div>
      </Drawer>
    </>
  );
};

export default LayoutHeader;
