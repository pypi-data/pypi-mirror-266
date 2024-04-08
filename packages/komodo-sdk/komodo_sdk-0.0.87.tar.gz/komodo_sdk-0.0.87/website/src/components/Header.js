"use client";
import React, { useContext } from "react";
import Select from "react-select";
import roleContext from "../contexts/roleContext";
import { useNavigate } from "react-router-dom";

const Header = () => {
  const navigate = useNavigate();
  const selectContext = useContext(roleContext);

  function handleChange(val) {
    const user = JSON.parse(localStorage.getItem("komodoUser"));
    localStorage.setItem(
      "komodoUser",
      JSON.stringify({ ...user, select: val })
    );
    selectContext?.setReactSelect(val);
    selectContext?.setChatGuid("");
    selectContext?.setChatHistory(false);
    selectContext?.setList([]);
    navigate("/chat");
  }

  const style = {
    control: (base) => ({
      ...base,
      cursor: "pointer",
      border: "0",
      fontSize: "21px",
      fontFamily: "Cerebri Sans",
      boxShadow: "none",
      " &: hover": {
        border: "0",
      },
    }),
    option: (base, { isSelected, isFocused }) => ({
      ...base,
      backgroundColor: isFocused ? "var(--primary-color)" : "#ffffff",
      cursor: "pointer",
      color: isFocused ? "#fff" : "#000",
      " &:hover": {
        backgroundColor: "var(--secondary-color)",
        color: "#000",
      },
    }),
    placeholder: (defaultStyles) => {
      return {
        ...defaultStyles,
        fontSize: "21px",
      };
    },
  };
  // console.log(
  //   "selectContext?.agentList?.agents :>> ",
  //   selectContext?.agentList?.agents
  // );
  // const agents = selectContext?.agentList?.agents || [];

  // const options = agents.map(agent => ({
  //   value: agent.shortcode,
  //   label: agent.name
  // }));

  // flex flex-row md:flex-col-reverse justify-between border-b-[0.5px] border-[#CDCDCD] h-[93px] md:h-auto items-center px-5 md:px-0 md:mx-4 sm:mx-2
  return (
    <div className="flex flex-row md:flex-col-reverse justify-between border-b-[0.5px] border-[#CDCDCD] h-[93px] items-center px-5 xl:justify-center">
      <div className="w-full xl:flex xl:justify-center xl:items-center xl:flex-col sm:ms-20">
        {selectContext?.reactSelect?.purpose !== undefined ? (
          <>
            <div className="w-fit">
              <Select
                className="font-cerebriregular selectstyle"
                value={selectContext?.reactSelect}
                onChange={handleChange}
                options={selectContext?.agentList?.agents}
                // options={selectContext?.agentList?.agents.map(agent => ({
                //   value: agent.name,
                //   label: agent.name
                // }))}
                styles={style}
                getOptionLabel={(agent) => agent["name"]}
                getOptionValue={(agent) => agent["email"]}
              />
            </div>
            <p
              className="m-[2px] font-cerebriregular xl:-ms-4 xs:ms-0 xs:text-center sm:text-[15px] subtitle cursor-pointer"
              title={selectContext?.reactSelect?.purpose || ""}
            >
              {selectContext?.reactSelect?.purpose || ""}
            </p>
          </>
        ) : null}
      </div>
      <div className="pr-1 sm:w-[90%] md:w-[95%] md:ml-10 w-full xl:hidden">
        <div className="flex items-center justify-end space-x-2 w-full">
          <h1 className="text-3xl font-cerebrisemibold">
            {selectContext?.company}
          </h1>
        </div>
        <div className="text-[18px] mt-1 font-cerebriregular text-end">
          <p>
            {selectContext?.agentList?.name ? (
              <span>{selectContext?.agentList?.name}</span>
            ) : (
              <span className="opacity-0">{selectContext?.company}</span>
            )}
          </p>
        </div>
      </div>
    </div>
  );
};

export default Header;
