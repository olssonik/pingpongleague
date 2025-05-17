const Footer = () => {
  return (
    <footer className="bg-slate-800 text-white/70 py-8 mt-12">
      <div className="container mx-auto px-4">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="mb-4 md:mb-0">
            <div className="flex items-center">
              <i className="fas fa-table-tennis-paddle-ball text-[#22c55e] mr-2"></i>
              <span className="font-bold text-white">OBC Table Tennis League</span>
            </div>
            <p className="text-sm mt-2">Tracking ping pong greatness since 2023</p>
          </div>
          <div className="text-sm">
            <p>&copy; {new Date().getFullYear()} OBC Table Tennis League. All rights reserved.</p>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
