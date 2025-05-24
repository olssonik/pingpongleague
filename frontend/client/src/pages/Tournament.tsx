import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";

export default function Tournament() {
  const [email, setEmail] = useState("");
  const { toast } = useToast();

  const handleNotifyMe = () => {
    // This would normally connect to a notification service
    if (!email || !email.includes('@')) {
      toast({
        title: "Invalid email",
        description: "Please enter a valid email address.",
        variant: "destructive",
      });
      return;
    }
    
    toast({
      title: "Notification Saved",
      description: "We'll notify you when tournaments are available!",
      variant: "default",
    });
    setEmail("");
  };

  return (
    <Card className="bg-white rounded-lg shadow-md mb-8">
      <CardContent className="p-6 text-center">
        <div className="flex flex-col items-center py-12">
          <div className="bg-primary/10 p-6 rounded-full mb-6">
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              className="h-16 w-16 text-primary" 
              fill="none" 
              viewBox="0 0 24 24" 
              stroke="currentColor"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth="1.5" 
                d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" 
              />
            </svg>
          </div>
          <h2 className="text-3xl font-bold text-slate-800 mb-4">Tournaments Coming Soon!</h2>
          <p className="text-slate-600 max-w-lg mb-8">
            We're working on bringing exciting tournaments to the OBC Table Tennis League. 
            Stay tuned for updates and get ready to compete!
          </p>
          
        </div>
      </CardContent>
    </Card>
  );
}
