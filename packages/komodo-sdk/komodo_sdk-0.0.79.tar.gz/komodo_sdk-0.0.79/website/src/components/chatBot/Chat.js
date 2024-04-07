import React, { useContext, useEffect, useRef, useState } from "react";
import AI from "../../assets/ai.png";
import { FiDownloadCloud } from "react-icons/fi";
import profile from "../../images/profile.png";
import send from "../../images/send.png";
import wave from "../../images/wave.png";
import { API_Path } from "../../API/ApiComment";
import roleContext from "../../contexts/roleContext";
import { RiSendPlaneFill } from "react-icons/ri";
import { ErrorToast } from "../../helpers/Toast";
import { ApiGet, ApiPost } from "../../API/API_data";
import MarkdownRenderer from "react-markdown-renderer";
import { FaRegCircleStop } from "react-icons/fa6";
import EnhancedBot from "./EnhancedBot";
import TextareaAutosize from "react-textarea-autosize";
import { useLocation } from "react-router";
import axios from "axios";
import dots from "../../images/dots.png";

export const Chat = ({
  selectedItemName,
  selectedFileName,
  handleFileChange,
}) => {
  const user = JSON.parse(localStorage.getItem("komodoUser"));
  const chatContext = useContext(roleContext);
  const chatContainerRef = useRef(null);

  const [prompt, setPrompt] = useState("");
  const [text, setText] = useState("");
  const [fullMessage, setFullMessage] = useState("");
  const [allChatData, setAllChatData] = useState([]);
  const [newDetails, setNewDetails] = useState({ gId: "", chatRes: "" });
  const [send, setSend] = useState(false);
  const [apiActive, setApiActive] = useState(true);
  const location = useLocation();
  const pathnameParts = location.pathname.split("/");
  const id = pathnameParts[pathnameParts.length - 1];
  console.log("location :>> ", location);

  const stopRes = () => {
    setApiActive(false);
    setSend(false);
  };
  // const getConversationByGuid = async (guid) => {
  //     try {
  //         // setLoader(true)
  //         const res = await ApiGet(API_Path.getDeleteConversation + guid)
  //         if (res?.status === 200) {
  //             setAllChatData(res?.data[0]?.messages)
  //         }
  //     } catch (error) {
  //         console.log('user details get ::error', error)
  //         ErrorToast(error?.data?.detail || "Something went wrong")
  //     } finally {
  //         // setLoader(false)
  //     }
  // }
  // useEffect(() => {
  //     getConversationByGuid("bb6b917b-6608-42ea-8e25-c69c2004d374")
  // }, []);

  const scrollToBottom = () => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop =
        chatContainerRef.current.scrollHeight;
    }
  };

  useEffect(() => {
    if (fullMessage !== "") {
      setNewDetails((perState) => {
        return { ...perState, chatRes: fullMessage };
      });
    }
  }, [fullMessage]);

  useEffect(() => {
    scrollToBottom();
  }, [allChatData, newDetails, text, prompt, fullMessage]);

  // useEffect(() => {
  //   if (location?.pathname) {
  //     setText("");
  //     getConversationByGuid(location.pathname.split("/chatdoc/")[1]);
  //     setNewDetails({
  //       ...newDetails,
  //       gId: location.pathname.split("/chatdoc/")[1],
  //     });
  //   }
  // }, [location?.pathname]);

  // const getConversationByGuid = async (guid) => {
  //   try {
  //     // setLoader(true);
  //     const res = await ApiGet(API_Path.conversationsGetUrl(guid));
  //     if (res?.status === 200) {
  //       setAllChatData(res?.data[0]?.messages);
  //     }
  //   } catch (error) {
  //     console.log("user details get ::error", error);
  //     ErrorToast(error?.data?.detail || "Something went wrong");
  //   } finally {
  //     // setLoader(false);
  //   }
  //   scrollToBottom();
  // };

  const sendPrompt = async () => {
    if (prompt.trim() !== "") {
      if (newDetails.chatRes !== "") {
        setAllChatData((prevData) => [
          ...prevData,
          {
            sender: chatContext?.reactSelect?.shortcode,
            text: newDetails.chatRes,
          },
          { sender: user.email, text: prompt },
        ]);
        setNewDetails({ ...newDetails, chatRes: "" });
      } else {
        setAllChatData((prevData) => [
          ...prevData,
          { sender: user.email, text: prompt },
        ]);
      }
      setText(prompt);
    }
    setPrompt("");
    scrollToBottom();
    setSend(true);
    setApiActive(true);
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      sendPrompt();
    }
    // if (e.key === "Enter" && !e.shiftKey) {
    //   sendPrompt();
    //   e.preventDefault();
    // }
  };

  const fileInputRef = useRef(null);

  const uploadFile = async () => {
    fileInputRef.current.value = null;
    fileInputRef.current.click();
  };

  // const handleFileChange = async (event) => {
  //   const selectedFile = event.target.files[0];
  //   console.log('Selected file:', selectedFile);

  //   let formData = new FormData();
  //   formData.append('files', selectedFile);

  //   try {
  //     const user = JSON.parse(localStorage.getItem('komodoUser'))

  //     let headers = {
  //       "Content-Type": "multipart/form-data",
  //       "X-User-Email": user?.email,
  //     };
  //     axios
  //       .post(`${API_Path.addCollection}/upload_files/${id}`, formData, {
  //         headers: headers,
  //       })
  //       .then((response) => {
  //         console.log('response :>> ', response);
  //       })
  //       .catch((err) => {
  //         console.log('err :>> ', err);
  //       });
  //   } catch (error) {
  //     console.error("Error occurred while adding collection:", error);
  //   }
  // };

  return (
    <>
      {/* <div className="flex items-center justify-between px-4 py-[11.5px] border-b border-[#E8E9EA] h-[63px]">
        <div className="text-[#1C232D] text-[16px] font-cerebriMedium">
          <div className="text-[#1C232D] text-[16px] font-cerebriMedium">
            {selectedItemName
              ? selectedFileName
                ? `${selectedItemName} / ${selectedFileName}`
                : selectedItemName
              : ""}
          </div>
        </div>
        <div>
          <input
            type="file"
            ref={fileInputRef}
            style={{ display: "none" }}
            onChange={handleFileChange}
          />
          <div
            className="flex items-center gap-2 border border-customBorderDark py-2 px-5 rounded-lg cursor-pointer"
            onClick={uploadFile}
          >
            <FiDownloadCloud className="text-customColor text-[18px]" />
            <div className="text-customColor font-normal text-[14px] font-cerebri">
              Export saved
            </div>
          </div>
        </div>
      </div> */}
      <div className="h-[calc(100vh-177px)] pt-1 flex items-center flex-col">
        {/* <div className="h-[calc(100vh-239px)] px-5 pt-1"> */}
        <div
          className={`chatscreen h-[calc(100vh-140px)] overflow-auto scrollbar mt-8 ${
            location?.state?.openChat === true
              ? "w-full px-5"
              : "mx-8 w-[1017px] xl:w-[800px] lg:w-full md:mx-4 lg:px-4"
          }`}
          // className="chatscreen h-[calc(100vh-140px)] overflow-auto scrollbar mt-10 mx-8 w-[1017px] xl:w-[800px] lg:w-full md:mx-4 lg:px-4"
          ref={chatContainerRef}
        >
          {allChatData &&
            allChatData.length > 0 &&
            allChatData.map((val, index) => {
              return (
                <div key={index} className="flex flex-col">
                  {val?.sender === user.email && (
                    <div className="flex mb-2">
                      <div className="flex items-center max-w-[94%] mt-2 gap-5">
                        <img
                          src={profile}
                          className="w-[30px] h-[30px]"
                          alt=""
                        />
                        <div className="flex flex-col">
                          <div className="text-[16px] font-cerebriregular rounded-[10px] bg-customBg px-4 py-3 text-customColor">
                            {val?.text}
                          </div>

                          {/* {val?.time && message?.answer && (
                          <div className="text-blackText font-cerebri font-normal text-[12px] text-right mt-1">
                            {new Date(
                              message.time.seconds * 1000 +
                                message.time.nanoseconds / 1000000
                            ).toLocaleTimeString("en-US", {
                              hour: "2-digit",
                              minute: "2-digit",
                              hour12: true,
                            })}
                          </div>
                        )} */}
                        </div>
                      </div>
                    </div>
                  )}

                  {/* {message.answer && ( */}
                  {val?.sender === chatContext?.reactSelect?.shortcode && (
                    <div className="flex items-start w-full mt-2 gap-2">
                      <div className="bg-customBgDark p-1.5 rounded-full min-w-[31px] h-[30px] mt-2">
                        <img
                          src={wave}
                          alt="wave"
                          className="w-[20px] h-[20px]"
                        />
                      </div>
                      <div className="flex flex-col">
                        <div>
                          {/* {val?.text} */}
                          <MarkdownRenderer
                            markdown={val?.text}
                            className="font-cerebriregular text-[15px] px-3 text-blackText removemargin"
                          />
                          {/* {message.answer} */}
                        </div>

                        {/* {message.time && ( */}
                        <div className="text-blackText font-cerebri font-normal text-[12px] text-right mt-1">
                          {/* 10:11 */}
                        </div>
                        {/* )} */}
                      </div>
                    </div>
                  )}

                  {/* //   )} */}
                </div>
              );
            })}
          {text !== "" && (
            // {text !== "" && fullMessage && (
            <div className="flex items-start w-full mt-2 gap-2">
              <div className="bg-customBgDark p-1.5 rounded-full min-w-[31px] h-[30px] mt-2">
                <img src={wave} alt="wave" className="w-[20px] h-[20px]" />
              </div>
              <div className="flex flex-col">
                <div
                // className="text-[16px] font-cerebriregular rounded-[10px] bg-senderBG border border-borderSky px-3 py-2 text-blackText"
                // dangerouslySetInnerHTML={{
                //   __html: fullMessage.replace(/\n/g, "<br>"),
                // }}
                >
                  {/* <MarkdownRenderer
                    markdown={fullMessage}
                    className="font-cerebriregular text-[16px] rounded-[10px] bg-senderBG border border-borderSky px-3 py-2 text-blackText removemargin"
                  /> */}
                  <EnhancedBot
                    prompt={text}
                    guid={newDetails?.gId}
                    setNewDetails={setNewDetails}
                    setSend={setSend}
                    apiActive={apiActive}
                  />
                </div>

                {/* {message.time && ( */}
                <div className="text-blackText font-cerebri font-normal text-[12px] text-right mt-1">
                  {/* 10:11 */}
                </div>
                {/* )} */}
              </div>
            </div>
          )}
          <div className={`flex flex-col mt-4 mb-5 `}>
            {/* {recommendedQuestions.length > 0 &&
        recommendedQuestions.map((question, index) => (
        <div
          key={index}
          className="border border-[#D4E0E9] rounded-lg px-3 py-2 w-fit cursor-pointer mt-2"
          onClick={() => handleRecommendedQuestionClick(question)}
        >
          {question}
        </div>
        ))} */}
          </div>
        </div>
      </div>
      <div className="relative px-5 border-t-[0.5px] border-[#CDCDCD] py-5 flex items-center justify-center gap-4 bg-white">
        <div className="w-[14px] sm:w-[40px]">
          <img src={dots} alt="send" />
        </div>
        <input
          type="text"
          className="w-[892px] xl:w-[700px] border border-[#CFD4D8] rounded-md px-4 pt-[13px] pb-[10px] outline-none text-[14px] font-cerebriregular leading-[17.78px]"
          placeholder="Ask or generate anything..."
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          onKeyDown={handleKeyPress}
        />
        {/* <TextareaAutosize
          minRows={1}
          placeholder="Ask or generate anything..."
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          onKeyDown={handleKeyPress}
          className="w-[892px] xl:w-[700px] border rounded-lg bg-senderBG border-borderSky  py-3.5 px-4 outline-none text-[14px] font-cerebriregular leading-[17.78px]"
        /> */}
        {/* <span className="cursor-pointer " onClick={sendPrompt}>
          <img src={send} alt="" />
        </span> */}

        {/* <div
          className="cursor-pointer bg-customBgDark text-white flex items-center justify-center rounded-lg h-[47px] pl-2.5 pr-4"
          onClick={sendPrompt}
        >
          <RiSendPlaneFill className="text-[21px] rotate-45" />
        </div> */}
        <div>
          {!send ? (
            <div
              className="cursor-pointer bg-customBgDark text-white flex items-center justify-center rounded-lg h-[43px] pl-2.5 pr-4"
              onClick={sendPrompt}
            >
              <RiSendPlaneFill className="text-[21px] rotate-45" />
            </div>
          ) : (
            <div
              className="cursor-pointer bg-customBgDark text-white flex items-center justify-center rounded-lg h-[43px] px-3"
              onClick={stopRes}
            >
              <FaRegCircleStop className="text-[21px]" />
            </div>
          )}
        </div>
      </div>
    </>
  );
};
