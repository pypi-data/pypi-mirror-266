import React from 'react';

  const CustomInput=({ label, placeholder, onChange,value }) => {
  return (
    <div className="font-cerebriregular">
      <label className="block mb-1 text-[18px]">{label}</label>
      <input
        id={label}
        type="text"
        value={value}
        className="border rounded-[10px] px-4 py-3 w-full bg-customBg border-customBorder text-[16px]"
        placeholder={placeholder}
        onChange={onChange}
      />
    </div>
  );
}
export default CustomInput