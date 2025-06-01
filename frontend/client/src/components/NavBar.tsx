import { Link, useLocation } from "wouter";

export default function NavBar() {
  const [location] = useLocation();

  const isActive = (path: string) => {
    if (path === "/" && location === "/") return true;
    if (path !== "/" && location.startsWith(path)) return true;
    return false;
  };

  return (
    <header className="bg-white shadow-md">
      <div className="container mx-auto px-4 py-4">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="flex items-center mb-4 md:mb-0">
            <div className="bg-primary p-2 rounded-md mr-3">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-6 w-6 text-white"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 0 0-2.456 2.456ZM16.894 20.567 16.5 21.75l-.394-1.183a2.25 2.25 0 0 0-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 0 0 1.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 0 0 1.423 1.423l1.183.394-1.183.394a2.25 2.25 0 0 0-1.423 1.423Z"
                />
              </svg>
            </div>
            <h1 className="text-2xl font-bold text-slate-800">
              OBC Table Tennis League
            </h1>
          </div>

          <nav className="w-full md:w-auto">
            <ul className="flex justify-between md:space-x-8 text-slate-600 font-medium">
              <li className="px-2 py-1">
                <Link href="/">
                  <a className={`py-1 px-1 ${isActive("/") ? "active-nav" : "hover:text-primary"}`}>
                    Dashboard
                  </a>
                </Link>
              </li>
              <li className="px-2 py-1">
                <Link href="/players">
                  <a className={`py-1 px-1 ${isActive("/players") ? "active-nav" : "hover:text-primary"}`}>
                    Players
                  </a>
                </Link>
              </li>
              <li className="px-2 py-1">
                <Link href="/games">
                  <a className={`py-1 px-1 ${isActive("/games") ? "active-nav" : "hover:text-primary"}`}>
                    Games
                  </a>
                </Link>
              </li>
              <li className="px-2 py-1">
                <Link href="/tournament">
                  <a className={`py-1 px-1 ${isActive("/tournament") ? "active-nav" : "hover:text-primary"}`}>
                    Tournament
                  </a>
                </Link>
              </li>
            </ul>
          </nav>
        </div>
      </div>
    </header>
  );
}
