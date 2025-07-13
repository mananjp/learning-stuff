import { Avatar } from '@mantine/core';

export function UserInfoIcons({ avatar, name, role, email, phone, info, github }) {
  return (
    <div className="flex gap-1 p-4 bg-white rounded-2xl shadow-md max-w border border-slate-100">
      <img
        src={avatar}
        className="shadow-lg border rounded-2xl h-70 border-slate-200"
        alt={name}
      />
      <div className="flex-1 w-full">
        {/* Name */}
        <div className="text-2xl pl-5 pr-10 font-semibold text-slate-900 truncate">
          {name}
        </div>
        {/* Role */}
        <div className="text-xs uppercase pl-5 font-bold text-slate-500 mb-1 tracking-wider">
          {role}
        </div>
        {/* Bio */}
        {info && (
          <p className="mt-3 text-sm text-slate-500 ml-3 leading-relaxed rounded p-2">
            {info}
          </p>
        )}
        {/* Email */}
        <div className="flex items-center mt-1 ml-5 gap-2">
          <span className="text-base text-blue-400">@</span>
          <a
            href={`mailto:${email}?subject=Hello%20${encodeURIComponent(name)}&body=Hi%20${encodeURIComponent(name)},%0A%0AI%20would%20like%20to%20connect%20with%20you!`}
            className="text-xs text-slate-600 break-all hover:text-blue-500 transition-colors"
          >
            {email}
          </a>
        </div>
        {/* Phone */}
        <div className="flex items-center mt-1 ml-5 gap-2">
          <span className="text-base text-blue-400"></span>
          <span className="text-xs text-slate-600 break-all">{phone}</span>
        </div>
        {/* Github */}
        <div className="flex items-center mt-1 ml-5 gap-2">
          <img
            src="https://cdn-icons-png.flaticon.com/512/25/25231.png"
            alt="github icon"
            className="w-4 h-4 opacity-80 hover:opacity-100 transition-opacity"
          />
          <a
            href={github}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-slate-600 hover:text-blue-500 break-all transition-colors"
          >
            {github}
          </a>
        </div>
      </div>
    </div>
  );
}
