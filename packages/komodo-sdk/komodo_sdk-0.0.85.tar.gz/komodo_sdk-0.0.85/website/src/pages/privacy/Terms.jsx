import React from "react";
import Sidebar from "../../components/Sidebar";

const Terms = () => {
  return (
    <div className="flex font-cerebriregular">
      <div className="w-[77px] xl:w-[60px]">
        <Sidebar />
      </div>

      <div className="flex-1 flex-col h-[100vh] overflow-auto  ">
        <div className="h-100 border-b border-customGray w-[100%] px-8 py-4 flex flex-col justify-between gap-3">
          <h2 className="text-[26px] font-cerebri text-[#000000] leading-[27px]">Terms and Conditions</h2>

          <h6 className="text-[18px] font-cerebri text-blackText">Privacy Policy</h6>
        </div>
        <div className="px-6 py-3 flex-1">
          <div className="grid grid-cols-1">
            <div className="h-100 border-b border-customGray xl:w-[100%] w-[65%] py-7 flex flex-col justify-between gap-3">
              <h2 className="text-[21px] font-cerebri text-[#000000] leading-[27px]">
                Ownership of Site; Agreement to Terms of Use
              </h2>

              <h6 className="text-[17px] font-cerebri text-blackText break-words">
                Suggested text: Our website address is: https://abc.com/work/xyz/qrk/html/komodo/1/
              </h6>
            </div>

            <div className="h-100 border-b border-customGray xl:w-[100%] w-[65%] py-7 flex flex-col justify-between gap-3">
              <h2 className="text-[21px] font-cerebri text-[#000000] leading-[27px]">Content</h2>

              <h6 className="text-[17px] font-cerebri text-blackText">
                Suggested text: When visitors leave comments on the site we collect the data shown in the
                comments form, and also the visitor's IP address and browser user agent string to help spam
                detection.
              </h6>

              <h6 className="text-[17px] font-cerebri text-blackText">
                An anonymized string created from your email address (also called a hash) may be provided to
                the Gravatar service to see if you are using it. The Gravatar service privacy policy is
                available here: https://automattic.com/privacy/. After approval of your comment, your profile
                picture is visible to the public in the context of your comment.
              </h6>
            </div>

            <div className="h-100 border-b border-customGray xl:w-[100%] w-[65%] py-7 flex flex-col justify-between gap-3">
              <h2 className="text-[21px] font-cerebri text-[#000000] leading-[27px]">Your Use of the Site</h2>

              <h6 className="text-[17px] font-cerebri text-blackText">
                Suggested text: If you upload images to the website, you should avoid uploading images with
                embedded location data (EXIF GPS) included. Visitors to the website can download and extract
                any location data from images on the website.
              </h6>
            </div>

            <div className="h-100 border-b border-customGray xl:w-[100%] w-[65%] py-7 flex flex-col justify-between gap-3">
              <h2 className="text-[21px] font-cerebri text-[#000000] leading-[27px]">
                Purchases; Other Terms and Conditions
              </h2>

              <h6 className="text-[17px] font-cerebri text-blackText">
                Suggested text: If you leave a comment on our site you may opt-in to saving your name, email
                address and website in cookies. These are for your convenience so that you do not have to fill
                in your details again when you leave another comment. These cookies will last for one year.
              </h6>

              <h6 className="text-[17px] font-cerebri text-blackText">
                If you visit our login page, we will set a temporary cookie to determine if your browser
                accepts cookies. This cookie contains no personal data and is discarded when you close your
                browser.
              </h6>

              <h6 className="text-[17px] font-cerebri text-blackText">
                When you log in, we will also set up several cookies to save your login information and your
                screen display choices. Login cookies last for two days, and screen options cookies last for a
                year. If you select "Remember Me", your login will persist for two weeks. If you log out of
                your account, the login cookies will be removed.
              </h6>

              <h6 className="text-[17px] font-cerebri text-blackText">
                If you edit or publish an article, an additional cookie will be saved in your browser. This
                cookie includes no personal data and simply indicates the post ID of the article you just
                edited. It expires after 1 day.
              </h6>
            </div>

            <div className="h-100 border-b border-customGray xl:w-[100%] w-[65%] py-7 flex flex-col justify-between gap-3">
              <h2 className="text-[21px] font-cerebri text-[#000000] leading-[27px]">
                Accounts, Passwords and Security
              </h2>

              <h6 className="text-[17px] font-cerebri text-blackText">
                Suggested text: Articles on this site may include embedded content (e.g. videos, images,
                articles, etc.). Embedded content from other websites behaves in the exact same way as if the
                visitor has visited the other website.
              </h6>

              <h6 className="text-[17px] font-cerebri text-blackText">
                These websites may collect data about you, use cookies, embed additional third-party tracking,
                and monitor your interaction with that embedded content, including tracking your interaction
                with the embedded content if you have an account and are logged in to that website.
              </h6>
            </div>

            <div className="h-100 border-b border-customGray xl:w-[100%] w-[65%] py-7 flex flex-col justify-between gap-3">
              <h2 className="text-[21px] font-cerebri text-[#000000] leading-[27px]">Privacy</h2>

              <h6 className="text-[17px] font-cerebri text-blackText">
                Suggested text: If you request a password reset, your IP address will be included in the reset
                email.
              </h6>
            </div>

            <div className="h-100 border-b border-customGray xl:w-[100%] w-[65%] py-7 flex flex-col justify-between gap-3">
              <h2 className="text-[21px] font-cerebri text-[#000000] leading-[27px]">Disclaimers</h2>

              <h6 className="text-[17px] font-cerebri text-blackText">
                Suggested text: Articles on this site may include embedded content (e.g. videos, images,
                articles, etc.). Embedded content from other websites behaves in the exact same way as if the
                visitor has visited the other website.
              </h6>

              <h6 className="text-[17px] font-cerebri text-blackText">
                These websites may collect data about you, use cookies, embed additional third-party tracking,
                and monitor your interaction with that embedded content, including tracking your interaction
                with the embedded content if you have an account and are logged in to that website.
              </h6>
            </div>

            <div className="h-100 border-b border-customGray xl:w-[100%] w-[65%] py-7 flex flex-col justify-between gap-3">
              <h2 className="text-[21px] font-cerebri text-[#000000] leading-[27px]">
                Violation of These Terms of Use
              </h2>

              <h6 className="text-[17px] font-cerebri text-blackText">
                Suggested text: If you have an account on this site, or have left comments, you can request to
                receive an exported file of the personal data we hold about you, including any data you have
                provided to us. You can also request that we erase any personal data we hold about you. This
                does not include any data we are obliged to keep for administrative, legal, or security
                purposes.
              </h6>
            </div>

            <div className="h-100 xl:w-[100%] w-[65%] py-7 flex flex-col justify-between gap-3">
              <h2 className="text-[21px] font-cerebri text-[#000000] leading-[27px]">Miscellaneous</h2>

              <h6 className="text-[17px] font-cerebri text-blackText">
                Suggested text: Visitor comments may be checked through an automated spam detection service.
              </h6>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Terms;
