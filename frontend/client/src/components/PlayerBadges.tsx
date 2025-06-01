import { Achievement } from "@/lib/api";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

interface PlayerBadgesProps {
  achievements: Achievement[];
  size?: "small" | "large";
  maxDisplay?: number;
}

export default function PlayerBadges({ achievements, size = "small", maxDisplay }: PlayerBadgesProps) {
  if (!achievements || achievements.length === 0) {
    return null;
  }

  const displayAchievements = maxDisplay ? achievements.slice(0, maxDisplay) : achievements;
  const hasMore = maxDisplay && achievements.length > maxDisplay;

  const badgeSize = size === "small" ? "h-6 w-6 text-xs" : "h-10 w-10 text-lg";
  const containerSpacing = size === "small" ? "space-x-1" : "space-x-2";

  return (
    <TooltipProvider>
      <div className={`flex items-center ${containerSpacing}`}>
        {displayAchievements.map((achievement) => {
          const isImageUrl = achievement.icon_url.startsWith('http');
          const iconSize = size === "small" ? "h-4 w-4" : "h-6 w-6";
          
          return (
            <Tooltip key={achievement.badge_id}>
              <TooltipTrigger asChild>
                <div
                  className={`${badgeSize} rounded-full bg-yellow-100 border-2 border-yellow-300 flex items-center justify-center cursor-help hover:bg-yellow-200 transition-colors`}
                >
                  {isImageUrl ? (
                    <img 
                      src={achievement.icon_url} 
                      alt={achievement.name}
                      className={`${iconSize} object-contain`}
                      style={{ filter: 'brightness(0) saturate(100%) invert(27%) sepia(51%) saturate(2878%) hue-rotate(346deg) brightness(104%) contrast(97%)' }}
                    />
                  ) : (
                    <span className="font-medium">
                      {achievement.icon_url}
                    </span>
                  )}
                </div>
              </TooltipTrigger>
              <TooltipContent>
                <div className="text-center">
                  <div className="font-semibold">{achievement.name}</div>
                  <div className="text-sm text-slate-600">{achievement.description}</div>
                </div>
              </TooltipContent>
            </Tooltip>
          );
        })}
        
        {hasMore && (
          <div className={`${badgeSize} rounded-full bg-slate-200 border-2 border-slate-300 flex items-center justify-center`}>
            <span className="text-slate-600 font-medium">+{achievements.length - maxDisplay!}</span>
          </div>
        )}
      </div>
    </TooltipProvider>
  );
}