import { useEffect, useState } from "react";
import { useParams } from "wouter";
import { Card, CardContent } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";

export function TournamentsDetails() {
  const { id } = useParams<{ id: string }>();
  const [tournament, setTournament] = useState<{
    id: number;
    name: string;
    active: boolean;
    winner: string | null;
  } | null>(null);
  const { toast } = useToast();

  useEffect(() => {
    const fetchTournament = async () => {
      try {
        const res = await fetch(`http://localhost:3000/api/get_tournaments`);
        const data = await res.json();
        const found = data.tournaments.find((t) => String(t.id) === id);
        if (found) {
          setTournament(found);
        } else {
          toast({
            title: "Tournament not found",
            description: `No tournament found with id ${id}`,
            variant: "destructive",
          });
        }
      } catch {
        toast({
          title: "Error",
          description: "Failed to load tournament data.",
          variant: "destructive",
        });
      }
    };

    fetchTournament();
  }, [id]);

  if (!tournament) return (<>
    <div><p>HELLOO</p></div>
  </>);

  return (
    <Card className="bg-white rounded-lg shadow-md mt-8">
      <CardContent className="p-6">
        <h2 className="text-3xl font-bold mb-4">
          {tournament.name || "Untitled Tournament"}
        </h2>
        <p className="mb-2">ID: {tournament.id}</p>
        <p className="mb-2">Active: {tournament.active ? "Yes" : "No"}</p>
        <p className="mb-2">
          Winner: {tournament.winner ? tournament.winner : "TBD"}
        </p>
      </CardContent>
    </Card>
  );
}
