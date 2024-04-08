import React, { useContext, useEffect, useRef, useState } from "react";
import send from "../../images/send.png";
import PrimaryLayout from "../../layout/PrimaryLayout";
import profile from "../../images/profile.png";
import dots from "../../images/dots.png";
import roleContext from "../../contexts/roleContext";
import wave from "../../images/wave.png";
import EnhancedPrompt from "../../components/chat/EnhancedPrompt";
import MarkdownRenderer from "react-markdown-renderer";
import { RiSendPlaneFill } from "react-icons/ri";
import TextareaAutosize from "react-textarea-autosize";
import { FaRegCircleStop } from "react-icons/fa6";

const Chat = () => {
  const chatContext = useContext(roleContext);
  const user = JSON.parse(localStorage.getItem("komodoUser"));
  const [prompt, setPrompt] = useState("");
  const [text, setText] = useState("");
  const [allChatData, setAllChatData] = useState([]);
  const [newDetails, setNewDetails] = useState({ gId: "", chatRes: "" });
  const chatContainerRef = useRef(null);
  const [send, setSend] = useState(false);
  const [apiActive, setApiActive] = useState(true);
  const stopRes = () => {
    setApiActive(false);
    setSend(false);
  };
  const scrollToBottom = () => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop =
        chatContainerRef.current.scrollHeight;
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [allChatData, newDetails, text, prompt]);

  useEffect(() => {
    if (chatContext?.chatGuid !== "") {
      setNewDetails({ ...newDetails, gId: chatContext?.chatGuid });
    } else {
      setNewDetails({ ...newDetails, gId: "", chatRes: "" });
      // setAllChatData([]);
      if (!chatContext?.chatHistory) {
        setAllChatData([]);
      }
    }
  }, [chatContext?.chatGuid]);

  useEffect(() => {
    setAllChatData([]);
    setText("");
    setNewDetails({ gId: "", chatRes: "" });
    scrollToBottom();
  }, [chatContext?.reactSelect]);

  const sendPrompt = async () => {
    console.log("chatContext :>> ", chatContext);
    console.log("newDetails :>> ", newDetails);
    if (prompt.trim() !== "") {
      chatContext?.setChatHistory(true);
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
    if (e.key === "Enter" && !e.shiftKey) {
      sendPrompt();
      e.preventDefault();
    }
  };

  const getTimeOfDay = () => {
    const now = new Date();
    const hour = now.getHours();

    if (hour >= 5 && hour < 12) {
      return "Good Morning, ";
    } else if (hour >= 12 && hour < 18) {
      return "Good Afternoon, ";
    } else {
      return "Good Evening, ";
    }
  };

  return (
    <>
      <PrimaryLayout>
        <div className="h-[calc(100vh-96px)]">
          {chatContext?.chatHistory === true ? (
            <div className="flex">
              <div className="w-full flex items-center flex-col h-[calc(100vh-93px)]">
                <div
                  ref={chatContainerRef}
                  className="mt-10 mx-8 overflow-y-auto h-[calc(100vh-217px)] scrollbar w-[1017px] xl:w-[950px] lg:w-[800px] md:w-full md:mx-4 sm:mx-2 lg:px-4"
                  // className="mt-10 mx-8 overflow-y-auto h-[700px] scrollbar w-[1017px] xl:w-[950px] lg:w-[800px] md:w-full md:mx-4 sm:mx-2"
                >
                  {allChatData &&
                    allChatData.length &&
                    allChatData.map((val, i) => {
                      return (
                        <div className="mb-5" key={i}>
                          {val?.sender === user?.email && (
                            <div div className="flex gap-5 items-center">
                              <div>
                                <img
                                  src={profile}
                                  alt="profile"
                                  className="w-[30px] h-[30px]"
                                />
                              </div>
                              <div className="text-[15px] font-cerebriregular rounded-md bg-customBg px-4 py-3 text-customColor">
                                {val?.text}
                              </div>
                            </div>
                          )}
                          {val?.sender ===
                            chatContext?.reactSelect?.shortcode && (
                            <div>
                              <div className="flex gap-5">
                                <div>
                                  <div className="bg-customBgDark p-1.5 rounded-full w-[31px] h-[30px] mt-2">
                                    <img src={wave} alt="wave" className="" />
                                  </div>
                                </div>
                                <div className="w-fit text-[#495057] md:break-all">
                                  <MarkdownRenderer
                                    markdown={val?.text}
                                    className="font-cerebriregular text-[15px] text-justify removemargin"
                                  />
                                </div>
                              </div>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  {text !== "" && (
                    <div className="mb-7">
                      <div>
                        <div className="flex gap-5">
                          <div>
                            <div className="bg-customBgDark p-1.5 rounded-full w-[31px] h-[30px] mt-2">
                              <img src={wave} alt="wave" className="" />
                            </div>
                          </div>
                          <div className="w-fit text-[#495057] md:break-all">
                            <EnhancedPrompt
                              prompt={text}
                              guid={newDetails?.gId}
                              setNewDetails={setNewDetails}
                              setSend={setSend}
                              apiActive={apiActive}
                            />
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
                <div className="border-t-[0.5px] border-[#CDCDCD]">
                  <div className="flex gap-4 items-center justify-center py-5 w-full lg:w-[800px] mx-8 md:w-[700px] md:mx-4 sm:w-[400px] sm:mx-2 xxs:w-[350px]">
                    <div className="w-[25px]">
                      <img src={dots} alt="send" className="w-fit max-w-fit" />
                    </div>
                    {/* <textarea
                      type="text"
                      placeholder="Ask me anything..."
                      value={prompt}
                      onChange={(e) => setPrompt(e.target.value)}
                      onKeyDown={handleKeyPress}
                      className="w-[892px] h-[43px] border border-[#CFD4D8] rounded-md px-4 pt-3 text-[14px] font-cerebriregular leading-[17.78px] outline-none"
                    /> */}
                    <TextareaAutosize
                      minRows={1}
                      placeholder="Ask me anything..."
                      value={prompt}
                      onChange={(e) => setPrompt(e.target.value)}
                      onKeyDown={handleKeyPress}
                      className="w-[892px] xl:w-[700px] border border-[#CFD4D8] rounded-md px-4 pt-3 pb-[11px] text-[14px] font-cerebriregular leading-[17.78px] outline-none"
                    />
                    {/* <img
                      src={send}
                      alt="send"
                      onClick={sendPrompt}
                      className="cursor-pointer w-[44px] h-[43px]"
                    /> */}

                    <div>
                      {!send ? (
                        <div
                          className="cursor-pointer bg-customBgDark text-white flex items-center justify-center rounded-lg h-[43px] pl-2 pr-3.5"
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
                </div>
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-[calc(100%-137px)] ">
              <div className="w-full mx-60 xl:mx-0  flex items-center flex-col justify-center lg:w-[800px] px-28 md:w-[700px] md:mx-4 sm:w-[400px] sm:px-2 sm:mx-2 xxs:w-[350px] h-full lg:px-4">
                <h1 className="text-[23px] font-cerebri leading-[29.21px] text-[#495057] mb-4">
                  {getTimeOfDay() + user?.name}
                </h1>
                <div className="flex gap-4 w-full justify-between items-center">
                  {/* <textarea
                    type="text"
                    placeholder="Ask me anything..."
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    onKeyDown={handleKeyPress}
                    className="h-[43px] border border-[#CFD4D8] rounded-md px-4 pt-3 text-[15px] font-cerebriregular leading-[19.05px] outline-none w-full"
                  /> */}
                  <TextareaAutosize
                    minRows={1}
                    placeholder="Ask me anything..."
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    onKeyDown={handleKeyPress}
                    className="border border-[#CFD4D8] rounded-md px-4 pt-3 pb-[10px] text-[15px] font-cerebriregular leading-[19.05px] outline-none w-full"
                  />

                  <div>
                    {!send ? (
                      <div
                        className="cursor-pointer bg-customBgDark text-white flex items-center justify-center rounded-lg h-[43px] pl-2 pr-3.5"
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
              </div>
            </div>
          )}
        </div>
      </PrimaryLayout>
    </>
  );
};

export default Chat;
