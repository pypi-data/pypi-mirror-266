import React, { Children, useState } from "react";
import Sidebar from "../components/Sidebar";
import { BiMinus } from "react-icons/bi";
import menuIcon from "../assets/Frame.svg";
import Drawer from "react-modern-drawer";
import close from "../assets/close.svg";
import { FiPlus, FiSearch, FiXCircle } from "react-icons/fi";
import ChatBotSideBar from "../components/chatBot/ChatBotSideBar";
import { Chat } from "../components/chatBot/Chat";
import HeaderSideBar from "../components/HeaderSideBar";
import pdf from "../images/sample.pdf";
import DocViewer, { DocViewerRenderers } from "@cyntler/react-doc-viewer";
import Header from "../components/Header";
import { ApiGet } from "../API/API_data";
import { API_Path } from "../API/ApiComment";

const CollectionLayout = ({ children }) => {
  const uploadedFiles = [
    {
      lastModified: "2024-03-04, 10:30",
      name: "document1.pdf",
      type: "pdf",
      file: "path/to/document1.pdf",
      key: "unique_key_1",
    },
    {
      lastModified: "2024-03-04, 10:30",
      name: "image1.docs",
      type: "docs",
      file: "path/to/image1.docs",
      key: "unique_key_2",
    },
    {
      lastModified: "2024-03-04, 10:30",
      name: "spreadsheet1.text",
      type: "text",
      file: "path/to/spreadsheet1.text",
      key: "unique_key_3",
    },
    {
      lastModified: "2024-03-04, 10:30",
      name: "document1.pdf",
      type: "pdf",
      file: "path/to/document1.pdf",
      key: "unique_key_1",
    },
    {
      lastModified: "2024-03-04, 10:30",
      name: "image1.docs",
      type: "docs",
      file: "path/to/image1.docs",
      key: "unique_key_2",
    },
    {
      lastModified: "2024-03-04, 10:30",
      name: "spreadsheet1.text",
      type: "text",
      file: "path/to/spreadsheet1.text",
      key: "unique_key_3",
    },
  ];

  const [isCollections, setIsCollections] = useState(true);
  const [searchText, setSearchText] = useState("");
  const [isSearchVisible, setIsSearchVisible] = useState(false);
  const [numPages, setNumPages] = useState(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [selectedCollectionName, setSelectedCollectionName] = useState("");
  const [selectedFileName, setSelectedFileName] = useState("");
  // const [filesData, setFilesData] = useState({});
  // console.log("filesData :>> ", filesData);

  const docs = [{ uri: pdf }];

  const toggleDrawer = () => {
    setIsDrawerOpen(!isDrawerOpen);
  };

  return (
    <div className="flex lg:block">
      <div className="z-[999]">
        <img
          src={menuIcon}
          // className="hidden xl:flex w-[24px] h-[24px] m-3"
          className={`hidden xl:flex xl:absolute w-[27px] h-[27px] mx-4 my-8 ${
            isDrawerOpen === true ? "xl:hidden" : ""
          }`}
          onClick={toggleDrawer}
          alt=""
        />
      </div>

      <div className="xl:hidden w-1/5 font-cerebri flex border-r-[0.5px] border-[#CDCDCD]">
        <Sidebar />
        <ChatBotSideBar
          uploadedFiles={uploadedFiles}
          setIsCollections={setIsCollections}
          isCollections={isCollections}
          setSelectedCollectionName={setSelectedCollectionName}
          setSelectedFileName={setSelectedFileName}
          // setFilesData={setFilesData}
          // filesData={filesData}
          // getUserFiles={getUserFiles}
        />
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

          <ChatBotSideBar
            uploadedFiles={uploadedFiles}
            setIsCollections={setIsCollections}
            isCollections={isCollections}
            setSelectedCollectionName={setSelectedCollectionName}
            setSelectedFileName={setSelectedFileName}
            // setFilesData={setFilesData}
            // filesData={filesData}
            // getUserFiles={getUserFiles}
          />
        </div>
      </Drawer>

      <div className="col-span-6 h-screen xl:w-full w-4/5">
        <Header />
        {/* <div className="grid lg:grid-cols-1 grid-cols-2">
          <div className="col-span-1 xl:border-l xl:border-[#E8E9EA]">
            <Chat
              selectedItemName={selectedCollectionName}
              selectedFileName={selectedFileName}
            />
          </div>

          <div className="col-span-1 border-l border-[#E8E9EA]">
            <div
              className={`bg-[#FFFFFF] ${
                isCollections ? "" : "h-[calc(100vh-93px)]"
              }`}
            >
              <DocViewer
                pluginRenderers={DocViewerRenderers}
                // documents={filesData?.files.map(doc => ({ uri: doc.path }))}
                documents={docs}
                config={{
                  header: {
                    disableHeader: false,
                    disableFileName: true,
                    retainURLParams: false,
                  },
                }}
                // style={{ width: 500, height: 500 }}
              />
            </div>
          </div>
        </div> */}
        {children}
      </div>
    </div>
  );
};

export default CollectionLayout;
