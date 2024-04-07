import React, { useContext } from "react";
import bluetick from "../../assets/blueTick.svg";
import { Link } from "react-router-dom";
import chattick from '../../../src/images/chattick.png'
import { SlSocialLinkedin } from "react-icons/sl";
import { LuFacebook } from "react-icons/lu";
import { LuInstagram } from "react-icons/lu";
import LayoutHeader from "../../components/LayoutHeader";
import roleContext from '../../contexts/roleContext'

const Pricing = () => {
  const selectContext = useContext(roleContext);

  const firstCard = [
    "Up to 50 Files",
    "Monthly questions limit",
    "Invite team members",
    "New feature early access",
    "Customer support",
    "Max file size",
    "1000 Visiters",
  ];
  return (
    <div>
      <div className="px-[100px] xl:px-[60px] lg:px-[40px] sm:px-3 sm:py-3 bg-cover bg-no-repeat bg-center" style={{ backgroundImage: "url('/pricingBg.png')" }}>
        <LayoutHeader />
        <div className="pb-7 h-[calc(100vh-70px)] overflow-auto scrollbar">
          <div className="text-center pt-16 pb-20 flex flex-col gap-2 w-[600px] m-auto sm:w-[370px]">
            <h5 className="text-customBlue text-[18px] font-medium">PRICING</h5>
            <h1 className="text-[34px] font-cerebribold">Choose your plan</h1>
            <div>
              <p className="text-[#797C8C] text-[16px] pb-1">
                Boost your productivity and use our AI tools to summarize Word
                documents
                {/* </p>
            <p className="text-[#797C8C] text-[16px]"> */}
                PDF and PowerPoint presentations and more.
              </p>
            </div>
            <div className="flex justify-center gap-4 items-center">
              <p>Monthly</p>

              <label className="inline-flex items-center cursor-pointer">
                <input type="checkbox" value="" className="sr-only peer" />
                <div className="relative w-12 h-7 bg-white peer-focus:outline-none rounded-full peer dark:bg-white peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white peer-checked:after:bg-white after:content-[''] after:absolute after:top-[4px] after:start-[2px] after:bg-customBlue after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
              </label>
              <p className="text-[#797C8C]">Yearly</p>
              <div className="rounded-[43px] text-customBlue border border-customBlue px-3 py-1">
                20% OFF
              </div>
            </div>
          </div>
          <div className="flex lg:flex-wrap xl:gap-5 lg:gap-10 gap-10 justify-center items-end md:flex-col md:items-center">
            <div className="border border-[#C7D8FD] w-[307px] h-[784] rounded-[26px] bg-white p-[46px]">
              <h2 className="text-[20px] font-cerebriMedium text-center">Starter</h2>
              <h1 className="text-[34px] font-cerebriMedium text-center">
                $48
                <span className="text-[16px] text-[#797C8C] font-cerebri">
                  / MO
                </span>
              </h1>
              <div className="my-5">
                {firstCard?.map((item) => {
                  return (
                    <div className="flex items-center gap-3">
                      <img src={bluetick} className="w-[17px] h-[11px]" />
                      <p className="text-[#3C3C3C]">{item}</p>
                    </div>
                  );
                })}
              </div>

              <button className="bg-customBlue py-2 px-5 text-white rounded-[10px] w-full ">
                Get started
              </button>
            </div>
            <div className="border border-[#C7D8FD] w-[307px] h-[800] rounded-[26px] text-white bg-[#1E2B45] ">
              <div className="bg-customBlue p-2 rounded-t-[26px] text-center">
                Most Popular
              </div>
              <div className="p-[46px]">
                <h2 className="text-[20px] font-cerebriMedium text-center">Starter</h2>
                <h1 className="text-[34px] font-cerebriMedium text-center">
                  $48
                  <span className="text-[16px]  font-cerebri">
                    / MO
                  </span>
                </h1>
                <div className="my-5">
                  {firstCard?.map((item) => {
                    return (
                      <div className="flex items-center gap-3">
                        <img src={bluetick} className="w-[17px] h-[11px]" />
                        <p className="">{item}</p>
                      </div>
                    );
                  })}
                </div>

                <button className="bg-customBlue py-2 px-5 text-white rounded-[10px] w-full ">
                  Get started
                </button>
              </div>

            </div>
            <div className="border border-[#C7D8FD] w-[307px] h-[784] rounded-[26px] bg-white p-[46px]">
              <h2 className="text-[20px] font-cerebriMedium text-center">Enterprice</h2>
              <h1 className="text-[34px] font-cerebriMedium text-center">
                Custom
                {/* <span className="text-[16px] text-[#797C8C] font-cerebri">
                / MO
              </span> */}
              </h1>
              <div className="my-5">
                {firstCard?.map((item) => {
                  return (
                    <div className="flex items-center gap-3">
                      <img src={bluetick} className="w-[17px] h-[11px]" />
                      <p className="text-[#3C3C3C]">{item}</p>
                    </div>
                  );
                })}
              </div>

              <button className="bg-customBlue py-2 px-5 text-white rounded-[10px] w-full ">
                Get started
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className='py-20 mt-3 px-20 md:px-10' style={{ backgroundImage: "url('/faqbg.png')" }}>
        <div className='flex justify-center items-center flex-col leading-[24px]'>
          <h2 className='text-[#316FF6] text-[18px] font-cerebri'>FAQ</h2>
          <h1 className='text-[#000000] text-[48px] font-cerebri mt-7 md:text-[30px]'>Frequently asked question</h1>
          <p className='text-[#797C8C] text-[16px] font-cerebriregular mt-8'>Please feel free to reach out to us. We are always happy to assist you and provide any additional.</p>
        </div>
        <div className="max-w-screen-xl mx-auto  min-h-sceen">
          <div className="grid divide-y divide-neutral-200 max-w-7xl mx-auto mt-8">
            <div className="py-5">
              <details className="group">
                <summary className="flex justify-between items-center font-medium cursor-pointer list-none outline-none">
                  <span className='text-[#3C3C3C] text-[20px] font-cerebriregular leading-[24px]'>What is an AI writer website?</span>
                  <span className="transition group-open:rotate-180">
                    <svg fill="none" height="24" shape-rendering="geometricPrecision" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" viewBox="0 0 24 24" width="24"><path d="M6 9l6 6 6-6"></path>
                    </svg>
                  </span>
                </summary>
                <p className="text-neutral-600 mt-3 group-open:animate-fadeIn font-cerebriregular">
                  Lorem ipsum is placeholder text commonly used in the graphic, print, and publishing industries for previewing layouts and visual mockups.
                </p>
              </details>
            </div>
            <div className="py-5">
              <details className="group">
                <summary className="flex justify-between items-center font-medium cursor-pointer list-none outline-none">
                  <span className='text-[#3C3C3C] text-[20px] font-cerebriregular leading-[24px]'> How does  billing work?</span>
                  <span className="transition group-open:rotate-180">
                    <svg fill="none" height="24" shape-rendering="geometricPrecision" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" viewBox="0 0 24 24" width="24"><path d="M6 9l6 6 6-6"></path>
                    </svg>
                  </span>
                </summary>
                <p className="text-neutral-600 mt-3 group-open:animate-fadeIn font-cerebriregular">
                  Lorem ipsum is placeholder text commonly used in the graphic, print, and publishing industries for previewing layouts and visual mockups.
                </p>
              </details>
            </div>
            <div className="py-5">
              <details className="group">
                <summary className="flex justify-between items-center font-medium cursor-pointer list-none outline-none">
                  <span className='text-[#3C3C3C] text-[20px] font-cerebriregular leading-[24px]'> Can I get a refund for my subscription?</span>
                  <span className="transition group-open:rotate-180">
                    <svg fill="none" height="24" shape-rendering="geometricPrecision" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" viewBox="0 0 24 24" width="24"><path d="M6 9l6 6 6-6"></path>
                    </svg>
                  </span>
                </summary>
                <p className="text-neutral-600 mt-3 group-open:animate-fadeIn font-cerebriregular">
                  Lorem ipsum is placeholder text commonly used in the graphic, print, and publishing industries for previewing layouts and visual mockups.
                </p>
              </details>
            </div>
            <div className="py-5">
              <details className="group">
                <summary className="flex justify-between items-center font-medium cursor-pointer list-none outline-none">
                  <span className='text-[#3C3C3C] text-[20px] font-cerebriregular leading-[24px]'> How do I cancel my subscription?</span>
                  <span className="transition group-open:rotate-180">
                    <svg fill="none" height="24" shape-rendering="geometricPrecision" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" viewBox="0 0 24 24" width="24"><path d="M6 9l6 6 6-6"></path>
                    </svg>
                  </span>
                </summary>
                <p className="text-neutral-600 mt-3 group-open:animate-fadeIn font-cerebriregular">
                  Lorem ipsum is placeholder text commonly used in the graphic, print, and publishing industries for previewing layouts and visual mockups.
                </p>
              </details>
            </div>
            <div className="py-5">
              <details className="group">
                <summary className="flex justify-between items-center font-medium cursor-pointer list-none outline-none">
                  <span className='text-[#3C3C3C] text-[20px] font-cerebriregular leading-[24px]'> Can I try this platform for free?</span>
                  <span className="transition group-open:rotate-180">
                    <svg fill="none" height="24" shape-rendering="geometricPrecision" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" viewBox="0 0 24 24" width="24"><path d="M6 9l6 6 6-6"></path>
                    </svg>
                  </span>
                </summary>
                <p className="text-neutral-600 mt-3 group-open:animate-fadeIn font-cerebriregular">
                  Lorem ipsum is placeholder text commonly used in the graphic, print, and publishing industries for previewing layouts and visual mockups.
                </p>
              </details>
            </div>
          </div>
        </div>
      </div>

      <div className='py-16 px-[300px] xxl:px-20 md:px-10'>
        <div className='flex justify-between lg:flex-col'>
          <h1 className='text-[#000000] text-[38px] font-cerebri leading-[58px] xl:text-[30px]'>Get Instant Assistance with Our AI-Powered Komodo Chatbot</h1>
          <button className='text-[#FFFFFF] text-[18px] font-cerebri leading-[24px] bg-[#316FF6] rounded-md px-6 pt-3 pb-2 h-fit lg:w-fit lg:mb-5'>Started chatting now</button>
        </div>
        <p className='text-[#797C8C] text-[16px] font-cerebriregular leading-[24px]'>Write 10x faster, engage your audience, & never struggle with the blank page again.</p>
        <div className='mt-14 divide-x divide-neutral-200 flex items-center gap-14 lg:flex-col lg:divide-x-0 lg:items-start md:gap-5'>
          <div className='flex gap-3 items-center'>
            <img src={chattick} alt="chattick" />
            <p className='text-[#3C3C3C] text-[24px] font-cerebriregular leading-[24px] md:text-[20px]'>No credit card required</p>
          </div>
          <div className='flex gap-3 items-center ps-14 lg:ps-0'>
            <img src={chattick} alt="chattick" />
            <p className='text-[#3C3C3C] text-[24px] font-cerebriregular leading-[24px] md:text-[20px]'>2,000 free words per month</p>
          </div>
          <div className='flex gap-3 items-center ps-14 lg:ps-0'>
            <img src={chattick} alt="chattick" />
            <p className='text-[#3C3C3C] text-[24px] font-cerebriregular leading-[24px] md:text-[20px]'>90+ content types to explore</p>
          </div>
        </div>
      </div>

      <footer style={{ backgroundImage: "url('/footer.png')" }} className='px-[300px] xxl:px-20 lg:px-10'>
        <div className="mx-auto w-full max-w-screen-xl p-4 py-6 lg:py-8 md:p-0">
          <div className="md:flex md:justify-between py-14">
            <div className="grid grid-cols-4 gap-8 sm:gap-6 lg:grid-cols-2 sm:grid-cols-1">
              <div>
                <h1 className='text-[#000000] text-[34px] font-cerebri leading-[24px]'>{selectContext?.company}</h1>
                <p className='mt-5 text-[#797C8C] text-[16px] font-cerebriregular leading-[24px]'>A Magical Tool to Optimize you content<br /> for the first know who you're targeting.<br /> Identify your target audience.</p>
                <div className='text-[#316FF6] flex gap-4 mt-7' >
                  <div className='bg-[#FFFFFF] p-4 rounded-full w-fit'>
                    <SlSocialLinkedin className=' w-[16px] h-[16px] text-[#316FF6]' />
                  </div>
                  <div className='bg-[#FFFFFF] p-4 rounded-full w-fit'>
                    <LuFacebook className=' w-[16px] h-[16px] text-[#316FF6]' />
                  </div>
                  <div className='bg-[#FFFFFF] p-4 rounded-full w-fit'>
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <g clip-path="url(#clip0_180_2835)">
                        <path d="M9.4893 6.77491L15.3176 0H13.9365L8.87577 5.88256L4.8338 0H0.171875L6.28412 8.89547L0.171875 16H1.55307L6.8973 9.78782L11.1659 16H15.8278L9.48896 6.77491H9.4893ZM7.59756 8.97384L6.97826 8.08805L2.05073 1.03974H4.17217L8.14874 6.72795L8.76804 7.61374L13.9371 15.0075H11.8157L7.59756 8.97418V8.97384Z" fill="#316FF6" />
                      </g>
                      <defs>
                        <clipPath id="clip0_180_2835">
                          <rect width="16" height="16" fill="white" />
                        </clipPath>
                      </defs>
                    </svg>
                  </div>
                  <div className='bg-[#FFFFFF] p-4 rounded-full w-fit'>
                    <LuInstagram className=' w-[16px] h-[16px] text-[#316FF6]' />
                  </div>
                </div>
              </div>
              <div>
                <h2 className="text-[#000000] text-[24px] font-cerebri leading-[24px]">Quick Menu</h2>
                <ul className="mt-5 text-[#797C8C] text-[20px] font-cerebriregular leading-[24px]">
                  <li className="mb-4">Home</li>
                  <Link to='/pricing'>
                    <li className='mb-4 cursor-pointer'>Pricing</li>
                  </Link>
                  <li>Help Center</li>
                </ul>
              </div>
              <div>
                <h2 className="text-[#000000] text-[24px] font-cerebri leading-[24px]">Legal</h2>
                <ul className="mt-5 text-[#797C8C] text-[20px] font-cerebriregular leading-[24px]">
                  <li className="mb-4">Terms of service</li>
                  <li className='mb-4'>Privacy</li>
                </ul>
              </div>
              <div>
                <h2 className="text-[#000000] text-[24px] font-cerebri leading-[24px]">Newsletter</h2>
                <input type="text" placeholder='Enter your email' className='text-[#797C8C] text-[16px] font-cerebriregular leading-[24px] bg-[#FFFFFF] rounded-md py-4 px-7 mt-5 xl:px-3' />
                <button className='text-[#FFFFFF] text-[18px] font-cerebri leading-[24px] bg-[#316FF6] rounded-md px-6 pt-3 pb-2 h-fit mt-4'>Subscribe</button>
              </div>
            </div>
          </div>
          <hr className="my-6 border-[#a4becc] sm:mx-auto lg:my-8" />
          <div className="flex justify-center pt-2 pb-1 text-[#3C3C3C] text-[18px] font-cerebriregular leading-[24px]">
            KomodoAI© 2023. All Rights Reserved.
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Pricing;

