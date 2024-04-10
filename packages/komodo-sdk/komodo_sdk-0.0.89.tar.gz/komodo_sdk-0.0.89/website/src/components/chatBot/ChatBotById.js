import React, { useContext, useEffect, useRef, useState } from "react";
import { useLocation } from "react-router-dom";
import roleContext from "../../contexts/roleContext";
import { ApiGet } from "../../API/API_data";
import { API_Path } from "../../API/ApiComment";
import { ErrorToast } from "../../helpers/Toast";
import wave from "../../images/wave.png";
import dots from "../../images/dots.png";
import profile from "../../images/profile.png";
import MarkdownRenderer from "react-markdown-renderer";
import { FaRegCircleStop } from "react-icons/fa6";
import { RiSendPlaneFill } from "react-icons/ri";
import EnhancedBot from "./EnhancedBot";
import CollectionLayout from "../../layout/CollectionLayout";
import DocViewer, { DocViewerRenderers } from "@cyntler/react-doc-viewer";
import { Panel, PanelGroup, PanelResizeHandle } from "react-resizable-panels";
import DocumentView from "../DocumentView";


const ChatBotById = () => {
    const chatContext = useContext(roleContext);
    const [prompt, setPrompt] = useState("");
    const [text, setText] = useState("");
    const [allChatData, setAllChatData] = useState([]);
    const [send, setSend] = useState(false);
    const location = useLocation();
    const parts = location?.pathname.split('/');
    const chatId = parts[3];
    const user = JSON.parse(localStorage.getItem("komodoUser"));
    const [loader, setLoader] = useState(false);
    const [newDetails, setNewDetails] = useState({ gId: "", chatRes: "" });
    const chatContainerRef = useRef(null);
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
        if (location?.pathname) {
            setText("");
            getConversationByGuid(chatId);
            setNewDetails({
                ...newDetails,
                gId: chatId,
            });
        }
    }, [location?.pathname]);

    const getConversationByGuid = async (guid) => {
        console.log('guid :>> ', guid);
        try {
            setLoader(true);
            const res = await ApiGet(API_Path.conversationsGetUrl(guid));
            if (res?.status === 200) {
                setAllChatData(res?.data[0]?.messages);
            }
        } catch (error) {
            console.log("user details get ::error", error);
            ErrorToast(error?.data?.detail || "Something went wrong");
        } finally {
            setLoader(false);
        }
        scrollToBottom();
    };

    const sendPrompt = async () => {
        if (prompt.trim() !== "") {
            if (newDetails.chatRes !== "") {
                setAllChatData((prevData) => [
                    ...prevData,
                    { sender: chatContext?.reactSelect?.shortcode, text: newDetails.chatRes },
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
            sendMessage();
        }
    };

    const sendMessage = () => {
        // Here you can send the message wherever you need it
        const messageToSend = prompt.replace(/\\n/g, "\n");
        console.log("messageToSend", messageToSend);
        // You can clear the prompt after sending the message if needed
        // setPrompt('');
    };

    return (
        <>
            <CollectionLayout>
                <PanelGroup
                    autoSaveId="example"
                    direction="horizontal"
                    className="panelgroup"
                >
                    <Panel
                        defaultSize={50}
                        id="sources-explorer-panel"
                        // className="min-w-[30%]"
                        className={`xl:border-l xl:border-[#E8E9EA] ${chatContext?.isDoc === true
                            ? // location?.state?.openChat === true
                            "min-w-[30%] xl:w-full"
                            : "min-w-full"
                            }`}
                    >
                        <div
                        // className={`grid lg:grid-cols-1 ${location?.state?.openChat === true ? "grid-cols-2" : ""
                        //     }`}
                        >
                            <div
                            //  className={`xl:border-l xl:border-[#E8E9EA] ${location?.state?.openChat === true ? "col-span-1" : ""
                            //     }`}
                            >
                                <div className="h-[calc(100vh-177px)] pt-1 flex items-center flex-col">
                                    <div
                                        // className={`chatscreen h-[calc(100vh-140px)] overflow-auto scrollbar mt-8 mx-8 w-[1017px] xl:w-[800px] lg:w-full md:mx-4 lg:px-4`}
                                        className={`chatscreen h-[calc(100vh-140px)] overflow-auto scrollbar mt-8 ${chatContext?.isDoc === true
                                                // location?.state?.openChat === true
                                                ? "w-full px-5"
                                                : "mx-8 w-[1017px] xl:w-[800px] lg:w-full md:mx-4 lg:px-4"
                                            }`}
                                        // className={`chatscreen h-[calc(100vh-140px)] overflow-auto scrollbar mt-8 ${location?.state?.openChat === true
                                        //     ? "w-full px-5"
                                        //     : "mx-8 w-[1017px] xl:w-[800px] lg:w-full md:mx-4 lg:px-4"
                                        //     }`}
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
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        )}


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
                                                                        <MarkdownRenderer
                                                                            markdown={val?.text}
                                                                            className="font-cerebriregular text-[15px] px-3 text-blackText removemargin"
                                                                        />
                                                                    </div>

                                                                    <div className="text-blackText font-cerebri font-normal text-[12px] text-right mt-1">

                                                                    </div>
                                                                </div>
                                                            </div>
                                                        )}

                                                    </div>
                                                );
                                            })}
                                        {text !== "" && (
                                            <div className="flex items-start w-full mt-2 gap-2">
                                                <div className="bg-customBgDark p-1.5 rounded-full min-w-[31px] h-[30px] mt-2">
                                                    <img src={wave} alt="wave" className="w-[20px] h-[20px]" />
                                                </div>
                                                <div className="flex flex-col">
                                                    <div
                                                    >

                                                        <EnhancedBot
                                                            prompt={text}
                                                            guid={newDetails?.gId}
                                                            setNewDetails={setNewDetails}
                                                            setSend={setSend}
                                                            apiActive={apiActive}
                                                        />
                                                    </div>

                                                    <div className="text-blackText font-cerebri font-normal text-[12px] text-right mt-1">
                                                    </div>
                                                </div>
                                            </div>
                                        )}
                                        <div className={`flex flex-col mt-4 mb-5 `}>
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
                            </div>
                            {/* <div>
                        <div
                            className={`border-l border-[#E8E9EA] ${location?.state?.openChat === true ? "col-span-1 block" : "hidden"
                                }`}
                        >
                            <div className={`bg-[#FFFFFF] h-[calc(100vh-93px)] overflow-auto scrollbar px-3 `}>
                                <DocViewer
                                    pluginRenderers={DocViewerRenderers}
                                    documents={[{ uri: chatContext?.pdfURL }]}
                                    config={{
                                        header: {
                                            disableHeader: true,
                                            disableFileName: true,
                                            retainURLParams: false,
                                        },
                                    }}
                                />
                            </div>
                        </div>
                    </div> */}
                        </div>
                    </Panel>
                    <PanelResizeHandle />
                    <Panel
                        defaultSize={50}
                        id="console-panel"
                        className={`border-l border-[#E8E9EA] ${chatContext?.isDoc === true
                            ? // location?.state?.openChat === true
                            "w-[50%] block xl:w-full"
                            : "hidden"
                            }`}
                    >
                        <DocumentView />
                    </Panel>
                </PanelGroup>
            </CollectionLayout>
            <style>
                {`
                .EZDrawer__overlay {
                background-color: transparent !important;
                }
                `}
            </style>
        </>
    )
};

export default ChatBotById;
