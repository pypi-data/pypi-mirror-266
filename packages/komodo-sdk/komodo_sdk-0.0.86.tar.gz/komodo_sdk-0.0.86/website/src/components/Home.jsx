import React, { useContext } from 'react'
import { Link } from 'react-router-dom'
import { GoArrowRight } from "react-icons/go";
import chatimg from '../../src/images/chatimg.png'
import content from '../../src/images/content.png'
import user from '../../src/images/user.png'
import copy from '../../src/images/copy.png'
import summary from '../../src/images/summary.png'
import first from '../../src/images/first.png'
import second from '../../src/images/second.png'
import chatgpt from '../../src/images/chatgpt.png'
import tick from '../../src/images/tick.png'
import chattick from '../../src/images/chattick.png'
import { SlSocialLinkedin } from "react-icons/sl";
import { LuFacebook } from "react-icons/lu";
import { LuInstagram } from "react-icons/lu";
import LayoutHeader from './LayoutHeader';
import roleContext from '../contexts/roleContext'

const Home = () => {
    const komodoUser = JSON.parse(localStorage.getItem("komodoUser"));
    const selectContext = useContext(roleContext);

    return (
        <div>
            <div
                className="bg-cover bg-no-repeat bg-center px-[100px] xl:px-[60px] lg:px-[40px] sm:px-3 sm:py-3"
                style={{ backgroundImage: "url('/home.png')" }}
            >
                <div>
                    <LayoutHeader />
                </div>
                <div className='pt-7 flex justify-center items-center flex-col'>
                    <h2 className='text-[#316FF6] text-[18px] font-cerebriMedium leading-[24px]'>Komodo.ai MAKES CONTENT FAST & EASY</h2>
                    <h1 className='text-[#1E2B45] text-[78px] font-cerebribold leading-[24px] mt-12 xl:text-[60px] lg:text-[41px] lg:leading-[61px] lg:text-center sm:mt-4'>Write content 10x faster</h1>
                    <p className='text-[#797C8C] text-[18px] font-cerebriregular leading-[31px] mt-10 text-center max-w-[688px] sm:mt-4 '>Using advanced artificial intelligence and deep learning, Article Forge writes entire 1,500+ word articles automatically. From product descriptions.</p>
                    <button className='flex justify-center items-center w-fit gap-2 text-[#ffffff] text-[20px] font-cerebri leading-[24px] bg-[#316FF6] rounded-md px-8 pt-4 pb-3 mt-8'>Try {selectContext?.company} <GoArrowRight /></button>
                </div>
                <div className='mt-10'>
                    <img src={content} alt="content" className='absolute bottom-96 xl:bottom-[22rem] xl:static' />
                    <div className='flex justify-center mt-14 xl:mt-2'>
                        <img src={chatimg} alt="chatimg" />
                    </div>
                    <div className='xl:flex xl:items-center xl:justify-end xl:mt-5'>
                        <img src={user} alt="user" className='absolute bottom-24 right-20 xl:static' />
                    </div>
                </div>

            </div>

            <div className='mt-20 flex justify-center items-center flex-col lg:mx-10'>
                <div className='flex justify-center items-center flex-col leading-[24px]'>
                    <h2 className='text-[#316FF6] text-[18px] font-cerebri'>PRICING</h2>
                    <h1 className='text-[#000000] text-[48px] font-cerebri mt-7 lg:text-[40px] md:text-[30px] md:text-center md:leading-[48px]'>Instruct to our AI writing generate copy</h1>
                    <p className='text-[#797C8C] text-[16px] font-cerebriregular mt-8 max-w-[500px] text-center'>Let our AI assist with most time consuming to write blog articles, product descriptions and more.</p>
                </div>
                <div className='flex bg-[#EEF5FF] rounded-3xl w-fit mt-12 px-20 pt-16 pb-10 xl:flex-col md:px-5'>
                    <img src={copy} alt="copy" />
                    <div className='ps-20 lg:ps-0'>
                        <img src={first} alt="first" className='mt-14' />
                        <h1 className='text-[#000000] text-[38px] font-cerebri leading-[48px] mt-8 mb-3'>Generate copy in <br /> seconds</h1>
                        <p className='text-[#797C8C] text-[16px] font-cerebriregular leading-[27px]'>Generate many types of content in under 30 seconds by <br /> simply inserting a few input fields. Generate blog topic <br /> ideas, intros, ad copy, copywriting.</p>
                        <button className='flex justify-center items-center w-fit text-[#ffffff] text-[18px] font-cerebri leading-[24px] bg-[#316FF6] rounded-md px-6 pt-4 pb-3 mt-8'>Get Started</button>
                    </div>
                </div>
                <div className='flex bg-[#F1F1FF] rounded-3xl w-fit mt-12 px-20 pt-16 pb-10 xl:flex-col md:px-5'>
                    <div className='pe-20 lg:pe-0'>
                        <img src={second} alt="second" className='mt-14' />
                        <h1 className='text-[#000000] text-[38px] font-cerebri leading-[48px] mt-8 mb-3'>Summarize PowerPoint <br /> presentations and more</h1>
                        <p className='text-[#797C8C] text-[16px] font-cerebriregular leading-[27px]'>Use our AI to create presentations for you. Simply <br /> upload a document and ask SlideSpeak to generate a <br /> presentation based on the content.</p>
                        <button className='xl:mb-14 flex justify-center items-center w-fit text-[#ffffff] text-[18px] font-cerebri leading-[24px] bg-[#316FF6] rounded-md px-6 pt-4 pb-3 mt-8'>Get Started</button>
                    </div>
                    <img src={summary} alt="summary" />
                </div>
            </div>

            <div className='flex justify-center items-center mt-6 px-72 pt-16 pb-10 xxl:px-20 lg:flex-col md:px-10'>
                <img src={chatgpt} alt="chatgpt" className='xl:w-[400px] xl:h-[400px]' />
                <div className='ps-20 flex flex-col justify-center lg:ps-0'>
                    <p className='text-[#316FF6] text-[18px] font-cerebri leading-[24px]'>{selectContext?.company} HELP YOU TO CREATE CONTENT FAST</p>
                    <h1 className='text-[#000000] text-[38px] font-cerebri leading-[58px] mt-6 mb-3 md:text-[30px]'>As sleek as ChatGPT, but with the finesse of your documents."</h1>
                    <p className='text-[#797C8C] text-[16px] font-cerebriregular leading-[24px]'>Upload your Any Type documents and ask questions about the content.</p>
                    <div className='flex gap-3 items-center mt-12'><img src={tick} alt="tick" /><span className='text-[#3C3C3C] text-[20px] font-cerebriregular leading-[24px]'>Create brief descriptions</span></div>
                    <div className='flex gap-3 items-center mt-7'><img src={tick} alt="tick" /><span className='text-[#3C3C3C] text-[20px] font-cerebriregular leading-[24px]'>Create presentations</span></div>
                    <div className='flex gap-3 items-center mt-7'><img src={tick} alt="tick" /><span className='text-[#3C3C3C] text-[20px] font-cerebriregular leading-[24px]'>Feel free to inquire about absolutely anything...</span></div>
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

        </div >
    )
}

export default Home