import React, { useContext, useEffect, useRef, useState } from "react";
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
import txt from "../images/dummy.txt";
import DocViewer, { DocViewerRenderers } from "@cyntler/react-doc-viewer";
import Header from "../components/Header";
import CollectionLayout from "../layout/CollectionLayout";
import { useLocation, useNavigate } from "react-router";
import axios from "axios";
import { API_Path } from "../API/ApiComment";
import roleContext from "../contexts/roleContext";
import { RxHamburgerMenu } from "react-icons/rx";
import { IoCloseSharp } from "react-icons/io5";
import dots from "../images/dots.png";
import arrowLeft from "../assets/arrowLeft.svg";
import { ApiDelete, ApiGet, ApiPost } from "../API/API_data";
import { SuccessToast } from "../helpers/Toast";
import { Box } from "@mui/system";
import { Modal } from "@mui/material";
// import {
//   Document,
//   Page,
//   Text,
//   View,
//   StyleSheet,
//   PDFViewer,
// } from "@react-pdf/renderer";

// const styles = StyleSheet.create({
// page: {
//   flexDirection: 'row',
//   backgroundColor: '#E4E4E4',
// },
//   section: {
//     margin: 10,
//     padding: 10,
//     flexGrow: 1,
//   },
// });

const style = {
  position: "absolute",
  top: "50%",
  left: "50%",
  transform: "translate(-50%, -50%)",
  width: "fit-content",
  bgcolor: "#fff",
  boxShadow: 20,
  // p: 4,
  borderRadius: "20px",
  outline: "none",
};

const ChatBot = () => {
  // "https://nett.umich.edu/sites/default/files/docs/pdf_files_scan_create_reducefilesize.pdf"
  // "https://medicine-storage.s3.ap-southeast-2.amazonaws.com/pdfs/p9973001.pdf"

  // const docs = [{ uri: pdf }];

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

  const [collection, setCollection] = useState("");
  const [description, setDescription] = useState("");
  const [isCollections, setIsCollections] = useState(true);
  const [searchText, setSearchText] = useState("");
  const [isSearchVisible, setIsSearchVisible] = useState(false);
  const [numPages, setNumPages] = useState(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [selectedCollectionName, setSelectedCollectionName] = useState("");
  const [selectedFileName, setSelectedFileName] = useState("");
  const [filesData, setFilesData] = useState({});
  const contextFiles = useContext(roleContext);
  const handleDelete = (chatId, e) => {
    e.stopPropagation();
    setDeleteChat(true);
    setDeleteChatId(chatId);
  };

  const user = JSON.parse(localStorage.getItem("komodoUser"));
  const fileInputRef = useRef(null);

  const [open, setOpen] = useState(false);
  const location = useLocation();
  const pathnameParts = location.pathname.split("/");
  const id = pathnameParts[pathnameParts.length - 1];

  console.log("location :>> ", location);

  const [collect, setCollect] = useState([]);
  const [deleteChat, setDeleteChat] = useState(false);
  const [deleteChatId, setDeleteChatId] = useState(null);
  const navigate = useNavigate();

  // const docs = [{ uri: pdf }];

  // const pdfData = location?.state?.fileData; // This should be replaced with the actual base64 data

  // Convert the base64 encoded string to a blob
  // const blob = new Blob([atob(pdfData)], { type: "application/pdf" });
  // const url = URL.createObjectURL(blob);

  const toggleDrawer = () => {
    setIsDrawerOpen(!isDrawerOpen);
  };

  const handleSelectItem = (name) => {
    setSelectedCollectionName(name);
  };
  const handleSelectedFileName = (name) => {
    setSelectedFileName(name);
  };

  // const handleAddCollections = async () => {
  //   let body = {
  //     name: collection,
  //     description: description,
  //   };
  //   try {
  //     const response = await ApiPost(API_Path.collectionsAddUrl, body);
  //     if (response.status === 200) {
  //       // Handle success
  //       SuccessToast("Collection added successfully");
  //       setOpen(false);
  //       setCollection("");
  //       setDescription("");
  //       CollectionData();
  //     } else {
  //       // Handle error
  //       console.error("Failed to add collection");
  //     }
  //   } catch (error) {
  //     console.error("Error occurred while adding collection:", error);
  //   }
  // };

  // const CollectionData = async () => {
  //   try {
  //     const collection = await ApiGet(API_Path.collectionsGetUrl);
  //     setCollect(collection?.data);
  //   } catch (error) {
  //     console.log("error", error);
  //   }
  // };

  // useEffect(() => {
  //   CollectionData();
  // }, []);

  // const handleFileData = async (guid) => {
  //   try {
  //     const file = await ApiGet(API_Path.collectionsDownloadFileUrl(id, guid));
  //     // console.log("file :>> ", file);
  //   } catch (error) {
  //     console.log("user details get ::error", error);
  //   }
  // };

  // const handleChatDelete = async (id, e) => {
  //   e.stopPropagation();
  //   try {
  //     const file = await ApiDelete(API_Path.conversationsDeleteUrl(id));
  //     if (file?.status === 200) {
  //       SuccessToast("Deleted successfully");
  //       setDeleteChat(false);
  //       CollectionData();
  //     }
  //   } catch (error) {
  //     console.log("user details get ::error", error);
  //   }
  // };

  const handleOpen = () => setOpen(true);
  const handleClose = () => setOpen(false);

  const handleFileChange = async (event) => {
    const selectedFile = event.target.files[0];
    console.log("Selected file:", selectedFile);

    let formData = new FormData();
    formData.append("files", selectedFile);

    try {
      const user = JSON.parse(localStorage.getItem("komodoUser"));

      let headers = {
        "Content-Type": "multipart/form-data",
        "X-User-Email": user?.email,
      };
      axios
        .post(API_Path.collectionsUploadFilesUrl(id), formData, {
          headers: headers,
        })
        .then((response) => {
          contextFiles?.getUserFiles(id);
          SuccessToast("File uploaded successfully");
        })
        .catch((err) => {
          console.log("err :>> ", err);
        });
    } catch (error) {
      console.error("Error occurred while adding collection:", error);
    }
  };

  const handleClickOutside = (e) => {
    if (!["close", "close1"].includes(e?.target?.id)) {
      setDeleteChat(false);
    }
  };

  useEffect(() => {
    document.addEventListener("mousedown", handleClickOutside);

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  return (
    <>
      <CollectionLayout>
        {/* <div className="flex lg:block">
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
            setFilesData={setFilesData}
            filesData={filesData}
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
              setFilesData={setFilesData}
              filesData={filesData}
            />
          </div>
        </Drawer>

        <div className="col-span-6 h-screen xl:w-full w-4/5">
          <Header />
          <div className="grid lg:grid-cols-1 grid-cols-2">
            <div className="col-span-1 xl:border-l xl:border-[#E8E9EA]">
              <Chat
                selectedItemName={selectedCollectionName}
                selectedFileName={selectedFileName}
              />
            </div>

            <div className="col-span-1 border-l border-[#E8E9EA]">
              {
                isCollections
                  ? // <HeaderSideBar />
                    ""
                  : ""
                // <div className="flex items-center justify-between py-[19px] px-3 border-b border-[#E8E9EA]">
                //   <div className="flex items-center gap-4">
                //     <div className="text-[#1C232D] font-cerebri font-normal text-[16px]">
                //       <span className="bg-[#F2F4FE] px-3 py-1 rounded-lg">1</span> / 4
                //     </div>
                //   </div>

                //   <div className="flex items-center lg:gap-1 gap-3">
                //     <FiPlus className="text-[18px] cursor-pointer" />
                //     <div className="text-[#1C232D] text-[16px] font-cerebri font-normal bg-[#F2F4FE] rounded py-1/2 px-1">
                //       100%
                //     </div>
                //     <BiMinus className="text-[18px] cursor-pointer" />
                //   </div>

                //   <div className="flex items-center gap-2 relative">
                //     {isSearchVisible && (
                //       <input
                //         type="text"
                //         className="border md:hidden border-[#EEEFEF] py-[3px] -mt-1 -mb-1 px-4 rounded-lg outline-none text-[#808DA4] text-[16px] font-cerebriregular font-normal"
                //         placeholder="search"
                //         value={searchText}
                //         onChange={(e) => setSearchText(e.target.value)}
                //       />
                //     )}

                //     {searchText && isSearchVisible && (
                //       <span
                //         className="md:hidden absolute text-blackText right-8 top-1/2 transform -translate-y-1/2 cursor-pointer"
                //         onClick={() => setSearchText("")}
                //       >
                //         <FiXCircle className="text-[#A4A7AB] text-[20px]" />
                //       </span>
                //     )}

                //     <FiSearch
                //       className="text-[#A4A7AB] text-[20px] cursor-pointer"
                //       onClick={() => setIsSearchVisible(!isSearchVisible)}
                //     />
                //   </div>
                // </div>
              }

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
          </div>
        </div>
      </div> */}

        <div
          className={`grid lg:grid-cols-1 ${location?.state?.openChat === true ? "grid-cols-2" : ""
            }`}
        >
          {/* <div className="grid lg:grid-cols-1 grid-cols-2"> */}
          <div
            className={`xl:border-l xl:border-[#E8E9EA] ${location?.state?.openChat === true ? "col-span-1" : ""
              }`}
          >
            {/* <div className="col-span-1 xl:border-l xl:border-[#E8E9EA]"> */}
            <Chat
              selectedItemName={location?.state?.collectionName}
              // selectedItemName={selectedCollectionName}
              selectedFileName={selectedFileName}
              handleFileChange={handleFileChange}
            />
          </div>

          <div
            className={`border-l border-[#E8E9EA] ${location?.state?.openChat === true ? "col-span-1 block" : "hidden"
              }`}
          >
            {/* <div className="col-span-1 border-l border-[#E8E9EA]"> */}
            <div
              className={`bg-[#FFFFFF] h-[calc(100vh-93px)] overflow-auto scrollbar px-3 ${isCollections ? "" : "h-[calc(100vh-93px)]"
                }`}
            >
              <DocViewer
                pluginRenderers={DocViewerRenderers}
                // documents={docs}
                documents={[{ uri: contextFiles?.pdfURL }]}
                config={{
                  header: {
                    disableHeader: true,
                    disableFileName: true,
                    retainURLParams: false,
                  },
                }}
              />

              {/* <PDFViewer className="h-full w-full font-cerebriregular">
                <Document>
                  <Page size="A4" style={styles.page}>
                    <View style={styles.section}>
                      <Text>{contextFiles?.pdfData}</Text>
                    </View>
                  </Page>
                </Document>
              </PDFViewer> */}
            </div>

            {/* <div className="flex items-center justify-between py-[19px] px-3 border-b border-[#E8E9EA]">
              <div className="flex items-center gap-4">
                <div className="text-[#1C232D] font-cerebri font-normal text-[16px]">
                  <span className="bg-[#F2F4FE] px-3 py-1 rounded-lg">1</span> /
                  4
                </div>
              </div>
              <div className="flex items-center lg:gap-1 gap-3">
                <FiPlus className="text-[18px] cursor-pointer" />
                <div className="text-[#1C232D] text-[16px] font-cerebri font-normal bg-[#F2F4FE] rounded py-1/2 px-1">
                  100%
                </div>
                <BiMinus className="text-[18px] cursor-pointer" />
              </div>
              <div className="flex items-center gap-2 relative">
                {isSearchVisible && (
                  <input
                    type="text"
                    className="border md:hidden border-[#EEEFEF] py-[3px] -mt-1 -mb-1 px-4 rounded-lg outline-none text-[#808DA4] text-[16px] font-cerebriregular font-normal"
                    placeholder="search"
                    value={searchText}
                    onChange={(e) => setSearchText(e.target.value)}
                  />
                )}

                {searchText && isSearchVisible && (
                  <span
                    className="md:hidden absolute text-blackText right-8 top-1/2 transform -translate-y-1/2 cursor-pointer"
                    onClick={() => setSearchText("")}
                  >
                    <FiXCircle className="text-[#A4A7AB] text-[20px]" />
                  </span>
                )}

                <FiSearch
                  className="text-[#A4A7AB] text-[20px] cursor-pointer"
                  onClick={() => setIsSearchVisible(!isSearchVisible)}
                />

                <RxHamburgerMenu
                  className="text-[#A4A7AB] text-[20px] cursor-pointer ms-2"
                  onClick={toggleDrawer}
                />

                <Drawer
                  open={isDrawerOpen}
                  onClose={toggleDrawer}
                  direction="right"
                  className="chatDrawer h-[calc(100vh-156px)] collectionDraw"
                >
                  <div className="font-cerebri w-[-webkit-fill-available] py-4">
                    <div>
                      <div className="flex gap-3 items-center px-4">
                        <IoCloseSharp
                          className="w-[24px] h-[24px] cursor-pointer"
                          onClick={toggleDrawer}
                        />
                        <h1 className="text-[18px] font-cerebri text-[#3C3C3C] leading-[24px]">
                          Collection
                        </h1>
                      </div>
                      <div className="text-[18px] font-cerebriregular text-[#6A6A6A] leading-[24px] border-b-[1px] border-[#F6F6F9] py-4 px-4">
                        Files
                      </div>
                      <div className="h-[calc(100vh-180px)] overflow-auto scrollbar">
                        <div className="mt-5">
                          <div>
                            {isCollections ? (
                              <>
                                <div className="flex items-center justify-between px-5">
                                  <div className="text-blackText text-[18px] mb-3 -ml-2 font-cerebriMedium">
                                    Collections
                                  </div>
                                </div>
                                <div>
                                  <div className="sidebar h-[calc(100vh-305px)] overflow-auto">
                                    {collect.map((item, index) => {
                                      return (
                                        <div
                                          className={`flex items-center justify-between px-3 py-3 mt-1 cursor-pointer overflow-hidden`}
                                          onClick={() => {
                                            handleSelectItem(item?.name);
                                            contextFiles?.getUserFiles(
                                              item?.guid
                                            );
                                            navigate(`/chatdoc/${item?.guid}`);
                                          }}
                                          key={index}
                                        >
                                          <div
                                            key={index}
                                            className={`flex items-center gap-2 cursor-pointer`}
                                            onClick={() =>
                                              setIsCollections(false)
                                            }
                                          >
                                            <span className="bg-customBg p-2 rounded-[5px]">
                                              <svg
                                                width="20"
                                                height="20"
                                                viewBox="0 0 24 24"
                                                fill="none"
                                                xmlns="http://www.w3.org/2000/svg"
                                              >
                                                <path
                                                  d="M21.67 14.3L21.27 19.3C21.12 20.83 21 22 18.29 22H5.71001C3.00001 22 2.88001 20.83 2.73001 19.3L2.33001 14.3C2.25001 13.47 2.51001 12.7 2.98001 12.11C2.99001 12.1 2.99001 12.1 3.00001 12.09C3.55001 11.42 4.38001 11 5.31001 11H18.69C19.62 11 20.44 11.42 20.98 12.07C20.99 12.08 21 12.09 21 12.1C21.49 12.69 21.76 13.46 21.67 14.3Z"
                                                  stroke="var(--primary-color)"
                                                  stroke-width="1.5"
                                                  stroke-miterlimit="10"
                                                />
                                                <path
                                                  d="M3.5 11.43V6.28C3.5 2.88 4.35 2.03 7.75 2.03H9.02C10.29 2.03 10.58 2.41 11.06 3.05L12.33 4.75C12.65 5.17 12.84 5.43 13.69 5.43H16.24C19.64 5.43 20.49 6.28 20.49 9.68V11.47"
                                                  stroke="var(--primary-color)"
                                                  stroke-width="1.5"
                                                  stroke-miterlimit="10"
                                                  stroke-linecap="round"
                                                  stroke-linejoin="round"
                                                />
                                                <path
                                                  d="M9.43005 17H14.5701"
                                                  stroke="var(--primary-color)"
                                                  stroke-width="1.5"
                                                  stroke-miterlimit="10"
                                                  stroke-linecap="round"
                                                  stroke-linejoin="round"
                                                />
                                              </svg>
                                            </span>

                                            <div>
                                              <div
                                                title={item?.description}
                                                className="text-blackText font-medium font-cerebri text-[14px] w-[110px] whitespace-nowrap overflow-hidden text-ellipsis"
                                              >
                                                {item?.name}
                                              </div>
                                            </div>
                                          </div>
                                          <div>
                                            <img
                                              src={dots}
                                              alt="dots"
                                              className="min-w-[16px]"
                                              onClick={(e) =>
                                                handleDelete(item?.guid, e)
                                              }
                                            />
                                            <div className="absolute">
                                              {deleteChat &&
                                                deleteChatId === item?.guid && (
                                                  <div
                                                    id="close"
                                                    className="relative bg-white border rounded-md shadow-md text-center right-14"
                                                    onClick={(e) =>
                                                      handleChatDelete(
                                                        item?.guid,
                                                        e
                                                      )
                                                    }
                                                  >
                                                    <button
                                                      id="close1"
                                                      className="text-[#5A636C] text-[13px] font-cerebri leading-[30px] px-4 py-[2px] mt-1 cursor-pointer"
                                                    >
                                                      Delete
                                                    </button>
                                                  </div>
                                                )}
                                            </div>
                                          </div>
                                        </div>
                                      );
                                    })}
                                  </div>

                                  <div>
                                    <div
                                      className={`flex items-center gap-2 cursor-pointer px-5`}
                                    >
                                      <span className="bg-customBg p-2 rounded-[5px]">
                                        <svg
                                          width="20"
                                          height="20"
                                          viewBox="0 0 24 24"
                                          fill="none"
                                          xmlns="http://www.w3.org/2000/svg"
                                        >
                                          <path
                                            d="M21.67 14.3L21.27 19.3C21.12 20.83 21 22 18.29 22H5.71001C3.00001 22 2.88001 20.83 2.73001 19.3L2.33001 14.3C2.25001 13.47 2.51001 12.7 2.98001 12.11C2.99001 12.1 2.99001 12.1 3.00001 12.09C3.55001 11.42 4.38001 11 5.31001 11H18.69C19.62 11 20.44 11.42 20.98 12.07C20.99 12.08 21 12.09 21 12.1C21.49 12.69 21.76 13.46 21.67 14.3Z"
                                            stroke="var(--primary-color)"
                                            stroke-width="1.5"
                                            stroke-miterlimit="10"
                                          />
                                          <path
                                            d="M3.5 11.43V6.28C3.5 2.88 4.35 2.03 7.75 2.03H9.02C10.29 2.03 10.58 2.41 11.06 3.05L12.33 4.75C12.65 5.17 12.84 5.43 13.69 5.43H16.24C19.64 5.43 20.49 6.28 20.49 9.68V11.47"
                                            stroke="var(--primary-color)"
                                            stroke-width="1.5"
                                            stroke-miterlimit="10"
                                            stroke-linecap="round"
                                            stroke-linejoin="round"
                                          />
                                          <path
                                            d="M9.43005 17H14.5701"
                                            stroke="var(--primary-color)"
                                            stroke-width="1.5"
                                            stroke-miterlimit="10"
                                            stroke-linecap="round"
                                            stroke-linejoin="round"
                                          />
                                        </svg>
                                      </span>

                                      <div
                                        className="text-blackText font-medium font-cerebri text-[14px] w-[110px] whitespace-nowrap overflow-hidden text-ellipsis"
                                        onClick={handleOpen}
                                      >
                                        New Collection
                                      </div>
                                      <Modal
                                        open={open}
                                        onClose={handleClose}
                                        aria-labelledby="modal-modal-title"
                                        aria-describedby="modal-modal-description"
                                      >
                                        <Box sx={style}>
                                          <div className="font-cerebri text-[20px] text-[#3C3C3C] mb-5 px-[32px] pt-[32px]">
                                            Add Collection
                                          </div>
                                          <hr />
                                          <div className="px-[32px] pb-[32px]">
                                            <div>
                                              <h1 className="text-[#000000] text-[16px] font-cerebriregular leading-[24px] mb-1 mt-5">
                                                Name
                                              </h1>
                                              <input
                                                type="text"
                                                placeholder="Add collection name..."
                                                className="bg-customBg rounded-lg w-[604px] py-4 px-5 mb-4 font-cerebriregular border-none outline-none text-[#797C8C]"
                                                value={collection}
                                                onChange={(e) =>
                                                  setCollection(e.target.value)
                                                }
                                              />
                                            </div>
                                            <div>
                                              <h1 className="text-[#000000] text-[16px] font-cerebriregular leading-[24px] mb-1 mt-1">
                                                Description
                                              </h1>
                                              <input
                                                type="text"
                                                placeholder="Add description..."
                                                className="bg-customBg rounded-lg w-full py-4 px-5 mb-4 font-cerebriregular border-none outline-none text-[#797C8C]"
                                                value={description}
                                                onChange={(e) =>
                                                  setDescription(e.target.value)
                                                }
                                              />
                                            </div>

                                            <div className="flex items-center justify-end mt-4 gap-3">
                                              <button
                                                className="text-[18px] font-cerebriregular text-[#3C3C3C] border border-customBorder rounded-lg py-2 px-5 shadow-drop cursor-pointer"
                                                onClick={handleClose}
                                              >
                                                Cancel
                                              </button>

                                              <button
                                                className="text-[18px] font-cerebriregular text-[#FFFFFF] bg-customBgDark rounded-lg py-2 px-7 cursor-pointer"
                                                onClick={handleAddCollections}
                                              >
                                                Add
                                              </button>
                                            </div>
                                          </div>
                                        </Box>
                                      </Modal>
                                    </div>
                                  </div>
                                </div>
                              </>
                            ) : (
                              <>
                                <div className="py-3 px-5 flex flex-col gap-4 border-b border-customGray">
                                  <div
                                    className="text-blackText flex text-[18px] gap-2 -ml-2 font-cerebriMedium cursor-pointer "
                                    onClick={() => {
                                      setIsCollections(true);
                                      setSelectedFileName("");
                                      navigate(`/chatdoc`);
                                    }}
                                  >
                                    <img
                                      src={arrowLeft}
                                      className="w-5 h-5"
                                      alt=""
                                    />
                                    Collection
                                  </div>
                                  <span className="text-blackText text-[18px] font-cerebriMedium -ml-2">
                                    Files
                                  </span>
                                </div>

                                <div>
                                  <div className="sidebar h-[calc(100vh-290px)] overflow-auto">
                                    {contextFiles?.filesData?.files?.map(
                                      (val, index) => {
                                        return (
                                          <div
                                            className={`flex items-center justify-between px-3 py-2 mt-1 cursor-pointer overflow-hidden`}
                                            onClick={() => {
                                              handleSelectedFileName(val.name);
                                              handleFileData(val?.guid);
                                            }}
                                            key={index}
                                          >
                                            <div
                                              key={index}
                                              className={`flex items-center gap-2`}
                                            >
                                              <span className="bg-customBg p-2 rounded-[5px]">
                                                <svg
                                                  width="20"
                                                  height="20"
                                                  viewBox="0 0 43 43"
                                                  fill="none"
                                                  xmlns="http://www.w3.org/2000/svg"
                                                >
                                                  <path
                                                    d="M39.3829 11.3381L28.3937 0.348871C28.1972 0.1524 27.9306 0.0420192 27.6527 0.0419922H15.3449C8.70895 0.0419922 3.31026 5.44177 3.31026 12.0791V27.1549C3.31026 27.7337 3.7794 28.2028 4.35814 28.2028C4.93687 28.2028 5.40601 27.7337 5.40601 27.1549V12.0791C5.40601 6.59739 9.86457 2.13774 15.345 2.13774H26.6049V6.57144C26.6049 10.1717 29.534 13.1007 33.1343 13.1007H37.5941V30.9234C37.5941 36.4038 33.1345 40.8623 27.6528 40.8623H15.3449C9.86449 40.8623 5.40593 36.4038 5.40593 30.9234C5.40593 30.3446 4.93679 29.8755 4.35805 29.8755C3.77932 29.8755 3.31018 30.3446 3.31018 30.9234C3.31018 37.5593 8.70895 42.958 15.3448 42.958H27.6527C34.29 42.958 39.6898 37.5593 39.6898 30.9234V12.0791C39.6898 11.8011 39.5793 11.5346 39.3829 11.3381ZM28.7006 6.57136V3.61956L36.086 11.005H33.1343C30.6895 11.005 28.7006 9.01614 28.7006 6.57136Z"
                                                    fill="var(--primary-color)"
                                                  />
                                                  <path
                                                    d="M17.0071 22.795C17.2345 22.9857 17.4105 23.2313 17.5351 23.532C17.6671 23.8327 17.7331 24.1957 17.7331 24.621C17.7331 25.1197 17.6378 25.578 17.4471 25.996C17.2565 26.4067 16.9595 26.722 16.5561 26.942C16.4021 27.03 16.2371 27.0997 16.0611 27.151C15.8925 27.195 15.7238 27.228 15.5551 27.25C15.3865 27.272 15.2251 27.2867 15.0711 27.294C14.9171 27.294 14.7778 27.294 14.6531 27.294H13.8391V30H12.0241V22.157H14.6531C15.2251 22.157 15.6945 22.212 16.0611 22.322C16.4351 22.4247 16.7505 22.5823 17.0071 22.795ZM15.5771 25.545C15.8045 25.3837 15.9181 25.1123 15.9181 24.731C15.9181 24.5257 15.8851 24.357 15.8191 24.225C15.7605 24.0857 15.6761 23.9757 15.5661 23.895C15.4121 23.7923 15.2251 23.73 15.0051 23.708C14.7925 23.686 14.5908 23.675 14.4001 23.675H13.8391V25.776H14.4001C14.4881 25.776 14.5835 25.776 14.6861 25.776C14.7961 25.7687 14.9025 25.7577 15.0051 25.743C15.1151 25.7283 15.2178 25.7063 15.3131 25.677C15.4158 25.6477 15.5038 25.6037 15.5771 25.545ZM19.2558 30V22.157H21.7418C22.4018 22.157 22.9554 22.2193 23.4028 22.344C23.8574 22.4613 24.2498 22.6373 24.5798 22.872C25.0491 23.2093 25.3974 23.653 25.6248 24.203C25.8594 24.7457 25.9768 25.3727 25.9768 26.084C25.9768 26.7953 25.8594 27.4223 25.6248 27.965C25.3974 28.5077 25.0491 28.9477 24.5798 29.285C24.2498 29.5197 23.8574 29.6993 23.4028 29.824C22.9554 29.9413 22.4018 30 21.7418 30H19.2558ZM21.0708 28.416H21.7308C22.0681 28.416 22.3651 28.3793 22.6218 28.306C22.8858 28.2327 23.1131 28.13 23.3038 27.998C23.5898 27.8073 23.8024 27.5507 23.9418 27.228C24.0884 26.898 24.1618 26.5167 24.1618 26.084C24.1618 25.644 24.0884 25.2627 23.9418 24.94C23.8024 24.61 23.5898 24.3497 23.3038 24.159C22.9078 23.8877 22.3834 23.752 21.7308 23.752H21.0708V28.416ZM32.3891 23.752H29.4411V25.292H31.9821V26.865H29.4411V30H27.6261V22.157H32.3891V23.752Z"
                                                    fill="var(--primary-color)"
                                                  />
                                                </svg>
                                              </span>

                                              <div>
                                                <div className="text-blackText font-medium font-cerebri text-[14px] w-[110px] whitespace-nowrap overflow-hidden text-ellipsis">
                                                  {val.name}
                                                </div>
                                              </div>
                                            </div>
                                            <img
                                              src={dots}
                                              alt="dots"
                                              className="min-w-[16px]"
                                            />
                                          </div>
                                        );
                                      }
                                    )}
                                  </div>
                                </div>
                              </>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="mx-5 mb-3">
                      <h1 className="text-[18px] leading-[25.4px] font-cerebri text-[#495057]">
                        {user?.name}
                      </h1>
                    </div>
                  </div>
                </Drawer>
              </div>
            </div> */}
          </div>
        </div>
      </CollectionLayout>

      <style>
        {`
        .EZDrawer__overlay {
          background-color: transparent !important;
        }
        `}
      </style>
    </>
  );
};

export default ChatBot;
