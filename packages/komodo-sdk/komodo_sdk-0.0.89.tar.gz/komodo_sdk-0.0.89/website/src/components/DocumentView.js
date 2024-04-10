import React, { useContext } from "react";
import roleContext from "../contexts/roleContext";
import DocViewer, { DocViewerRenderers } from "@cyntler/react-doc-viewer";
import { OutTable } from "react-excel-renderer";

const DocumentView = () => {
  const contextFiles = useContext(roleContext);

  return (
    <div
      className={`bg-[#FFFFFF] h-[calc(100vh-93px)] overflow-auto scrollbarCustom px-3 `}
      // scrollbar - remove scrollbar
    >
      {contextFiles?.pdfURL ? (
        contextFiles?.pdfURL?.rows && contextFiles?.pdfURL?.cols ? (
          <OutTable
            data={contextFiles?.pdfURL?.rows || []}
            columns={contextFiles?.pdfURL?.cols || []}
            tableClassName="ExcelTable2007 border"
            tableHeaderRowClass="font-bold bg-blue-100"
          />
        ) : (
          <DocViewer
            pluginRenderers={DocViewerRenderers}
            documents={[{ uri: contextFiles?.pdfURL }]}
            config={{
              header: {
                disableHeader: true,
                disableFileName: false,
                retainURLParams: false,
              },
              pdfVerticalScrollByDefault: true,
              loadingRenderer: {
                overrideComponent: () => {
                  console.log("Loading...");
                  return <div>Loading Custom</div>;
                },
                showLoadingTimeout: true,
              },
              noRenderer: {
                overrideComponent: () => {
                  console.log("Error component override");
                  return <div>Error Custom</div>;
                },
              },
            }}
          />
        )
      ) : null}

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
  );
};

export default DocumentView;
