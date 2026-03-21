import * as React from "react";
import { cn } from "@/lib/utils";

export interface GlassButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  size?: "sm" | "default" | "lg";
  contentClassName?: string;
}

const sizeClasses = {
  sm: "px-4 py-2 text-sm",
  default: "px-6 py-3.5 text-base",
  lg: "px-8 py-4 text-lg",
};

export const GlassButton = React.forwardRef<HTMLButtonElement, GlassButtonProps>(
  ({ className, children, size = "default", contentClassName, ...props }, ref) => (
    <div className={cn("glass-button-wrap cursor-pointer rounded-full", className)}>
      <button className="glass-button relative isolate cursor-pointer rounded-full transition-all font-medium" ref={ref} {...props}>
        <span className={cn("glass-button-text relative block select-none tracking-tighter", sizeClasses[size], contentClassName)}>
          {children}
        </span>
      </button>
      <div className="glass-button-shadow rounded-full" />
    </div>
  )
);
GlassButton.displayName = "GlassButton";
