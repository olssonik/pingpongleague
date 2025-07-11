import { useEffect, useState } from "react";
import { useParams } from "wouter";

type Match = [string, string, string]; // [player1, player2, winner]
type Round = Match[];

export default function TournamentDetails() {
  const { id } = useParams();
  const [rounds, setRounds] = useState<Round[]>([]);
  const [error, setError] = useState("");
  const [display, setDisplay] = useState("");

  useEffect(() => {
    fetch(`/api/tournament/${id}`)
      .then((res) => {
        if (!res.ok) throw new Error("Fetch failed");
        return res.json();
      })
      .then((json) => {
        if (json.rounds) setRounds(json.rounds);
        else if (json.message) setDisplay(json.message);
      })
      .catch((e) => setError(e.message));
  }, [id]);

  if (error) return <div>Error: {error}</div>;
  if (display) return <div>{display}</div>;
  if (!rounds.length) return <div>Loading tournament...</div>;

  return (
    <div style={{ maxWidth: 600, margin: "auto" }}>
      <h2>Tournament Rounds</h2>
      {rounds.map((round, roundIdx) => (
        <div key={roundIdx} style={{ marginBottom: 24 }}>
          <h3>Round {roundIdx + 1}</h3>
          {round.map(([p1, p2, winner]: Match, matchIdx: number) => (
            <div
              key={matchIdx}
              style={{
                display: "flex",
                justifyContent: "space-between",
                marginBottom: 10,
                padding: 10,
                border: "1px solid #ccc",
                borderRadius: 6,
              }}
            >
              <div
                style={{
                  fontWeight: winner === p1 ? "bold" : "normal",
                  color: winner === p1 ? "green" : "black",
                }}
              >
                {p1}
              </div>
              <span>vs</span>
              <div
                style={{
                  fontWeight: winner === p2 ? "bold" : "normal",
                  color: winner === p2 ? "green" : "black",
                }}
              >
                {p2}
              </div>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}