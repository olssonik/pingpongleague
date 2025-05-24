interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

export default function Pagination({ currentPage, totalPages, onPageChange }: PaginationProps) {
  return (
    <div className="flex justify-center mt-6">
      <button 
        className={`${currentPage === 1 ? 'bg-slate-100 text-slate-600 cursor-not-allowed' : 'bg-slate-200 text-slate-800 hover:bg-slate-300'} px-3 py-1 rounded-md mx-1`}
        onClick={() => currentPage > 1 && onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
      >
        Previous
      </button>
      
      {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => (
        <button 
          key={page}
          className={`${currentPage === page ? 'bg-primary text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'} px-3 py-1 rounded-md mx-1`}
          onClick={() => onPageChange(page)}
        >
          {page}
        </button>
      ))}
      
      <button 
        className={`${currentPage === totalPages ? 'bg-slate-100 text-slate-600 cursor-not-allowed' : 'bg-slate-200 text-slate-800 hover:bg-slate-300'} px-3 py-1 rounded-md mx-1`}
        onClick={() => currentPage < totalPages && onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
      >
        Next
      </button>
    </div>
  );
}
