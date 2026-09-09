import { useEffect, useState, type ElementType, type ReactNode } from "react";
import { motion } from "motion/react";
import { cn } from "@/lib/utils";
import { usePrefersReducedMotion } from "@/lib/theme";

type Direction = "TOP" | "RIGHT" | "BOTTOM" | "LEFT";

const movingMap: Record<Direction, string> = {
  TOP: "radial-gradient(22% 60% at 50% 0%, var(--signal) 0%, transparent 100%)",
  LEFT: "radial-gradient(20% 60% at 0% 50%, var(--signal) 0%, transparent 100%)",
  BOTTOM: "radial-gradient(22% 60% at 50% 100%, var(--signal) 0%, transparent 100%)",
  RIGHT: "radial-gradient(20% 60% at 100% 50%, var(--signal) 0%, transparent 100%)",
};

const order: Direction[] = ["TOP", "LEFT", "BOTTOM", "RIGHT"];

/**
 * Animated hairline border that travels around a container on hover or focus.
 * Restyled for Filing Intelligence: warm signal accent, translucent interior,
 * 1px border, no glow.
 */
export function HoverBorderGradient({
  children,
  containerClassName,
  className,
  as: Tag = "div",
  duration = 1.6,
  active = false,
}: {
  children: ReactNode;
  containerClassName?: string;
  className?: string;
  as?: ElementType;
  duration?: number;
  /** Force the animated border on (e.g. while the inner input has focus). */
  active?: boolean;
}) {
  const [hovered, setHovered] = useState(false);
  const [direction, setDirection] = useState<Direction>("TOP");
  const reduced = usePrefersReducedMotion();
  const on = (hovered || active) && !reduced;

  useEffect(() => {
    if (!on) return;
    const id = window.setInterval(() => {
      setDirection((prev) => order[(order.indexOf(prev) + 1) % order.length]!);
    }, duration * 1000);
    return () => window.clearInterval(id);
  }, [on, duration]);

  return (
    <Tag
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      onFocus={() => setHovered(true)}
      onBlur={() => setHovered(false)}
      className={cn(
        "relative flex w-full items-center justify-center overflow-hidden rounded-full border border-border bg-surface/50 p-px transition-colors duration-300",
        (hovered || active) && "border-border-strong",
        containerClassName,
      )}
    >
      <div className={cn("relative z-10 w-full rounded-full bg-background/70 backdrop-blur-sm", className)}>
        {children}
      </div>
      <motion.div
        aria-hidden
        className="absolute inset-0 z-0 rounded-full"
        style={{ filter: "blur(2px)" }}
        initial={{ background: movingMap.TOP, opacity: 0 }}
        animate={{
          background: on ? movingMap[direction] : movingMap.TOP,
          opacity: on ? 0.85 : 0,
        }}
        transition={{ ease: "linear", duration: reduced ? 0 : duration }}
      />
    </Tag>
  );
}
