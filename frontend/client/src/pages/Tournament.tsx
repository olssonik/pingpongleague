import { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { Link, useLocation } from "wouter";


export default function Tournament() {
  const [tournaments, setTournaments] = useState([]);
  const { toast } = useToast();
  // const [location] = useLocation();

  const fetchTournaments = async () => {
    try {
      const res = await fetch("http://localhost:3000/api/get_tournaments");
      if (!res.ok) throw new Error("Failed to fetch tournaments");
      const data = await res.json();

      if (data.tournaments && data.tournaments.length > 0) {
        setTournaments(data.tournaments);
      } else {
        toast({
          title: "No tournaments found",
          description: "No tournaments are available at the moment.",
          variant: "default",
        });
        setTournaments([]);
      }
    } catch {
      toast({
        title: "Error",
        description: "Could not load tournaments. Try again later.",
        variant: "destructive",
      });
    } finally {
    }
  };

  useEffect(() => { fetchTournaments() }, []
  )
  return (
    <Card className="bg-white rounded-lg shadow-md mb-8">
      <CardContent className="p-6 text-center">
        <div className="py-12">
          <h2 className="text-3xl font-bold text-slate-800 mb-4">
            Upcoming OBC Tournaments
          </h2>
          <p className="text-slate-600 max-w-lg mx-auto mb-8">
            Check out the schedule and sign up to show your skills. Don’t miss out on the action!
          </p>

          {tournaments.length > 0 && (
            <table className="mt-8 w-full text-left border-collapse border border-gray-300">
              <thead>
                <tr>
                  <th className="border border-gray-300 px-4 py-2">Name</th>
                  <th className="border border-gray-300 px-4 py-2">Active</th>
                  <th className="border border-gray-300 px-4 py-2">Winner</th>
                  <th className="border border-gray-300 px-4 py-2">Select</th>
                </tr>
              </thead>
              <tbody>
                {tournaments.map(({ id, name, active, winner }) => (
                  <tr key={id}>
                    <td className="border border-gray-300 px-4 py-2">{name || "Untitled"}</td>
                    <td className="border border-gray-300 px-4 py-2">
                      {active ? "Yes" : "No"}
                    </td>
                    <td className="border border-gray-300 px-4 py-2">
                      {winner || "awaiting"}
                    </td>
                    <td className="border border-gray-300 px-4 py-2">
                      <Link to={`/tournament/${id}`} className="text-blue-600 hover:underline">
                        Select
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
