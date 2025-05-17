import { useState } from "react";
import { Link } from "wouter";

const Header = () => {
  const [activeTab, setActiveTab] = useState<string>("dashboard");

  return (
    <header className="bg-[#22c55e] text-white shadow-md">
      <div className="container mx-auto px-4 py-6 flex flex-col md:flex-row items-center justify-between">
        <div className="flex items-center mb-4 md:mb-0">
          <i className="fas fa-table-tennis-paddle-ball text-3xl mr-3"></i>
          <h1 className="text-2xl md:text-3xl font-bold">OBC Table Tennis League</h1>
        </div>
        <div>
          <nav className="flex">
            <Link href="/">
              <span 
                className={`px-4 py-2 font-medium border-b-2 cursor-pointer ${
                  activeTab === "dashboard" 
                    ? "border-white" 
                    : "border-transparent hover:border-white/70"
                }`}
                onClick={() => setActiveTab("dashboard")}
              >
                Dashboard
              </span>
            </Link>
            <Link href="/players">
              <span 
                className={`px-4 py-2 font-medium border-b-2 cursor-pointer ${
                  activeTab === "players" 
                    ? "border-white" 
                    : "border-transparent hover:border-white/70"
                }`}
                onClick={() => setActiveTab("players")}
              >
                Players
              </span>
            </Link>
            <Link href="/games">
              <span 
                className={`px-4 py-2 font-medium border-b-2 cursor-pointer ${
                  activeTab === "games" 
                    ? "border-white" 
                    : "border-transparent hover:border-white/70"
                }`}
                onClick={() => setActiveTab("games")}
              >
                Games
              </span>
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header;
