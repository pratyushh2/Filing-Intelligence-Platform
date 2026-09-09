import { useState, type ReactNode } from "react";
import { motion } from "motion/react";
import { cn } from "@/lib/utils";
import { usePrefersReducedMotion } from "@/lib/theme";

export type ImagesBadgeProps = {
  /** Optional label rendered under the folder. */
  text?: string;
  /** Up to three preview nodes (local SVG/CSS filing artifacts). */
  images: ReactNode[];
  className?: string;
  href?: string;
  target?: string;
  onSelect?: () => void;
  folderSize?: number;
  teaserImageSize?: number;
  hoverImageSize?: number;
  hoverTranslateY?: number;
  hoverSpread?: number;
  hoverRotation?: number;
  /** Optional external hover state (e.g. hovering the whole card). */
  hovered?: boolean;
};

const spring = { type: "spring" as const, stiffness: 320, damping: 26, mass: 0.7 };

/**
 * Folder badge: three filing previews peek out at rest, then fan upward,
 * spread, rotate and enlarge on hover while the folder front tilts flat.
 * Hover state is local to each instance.
 */
export function ImagesBadge({
  text,
  images,
  className,
  href,
  target,
  onSelect,
  folderSize = 88,
  teaserImageSize = 46,
  hoverImageSize = 74,
  hoverTranslateY = 74,
  hoverSpread = 58,
  hoverRotation = 11,
  hovered: hoveredProp,
}: ImagesBadgeProps) {
  const [hovered, setHovered] = useState(false);
  const reduced = usePrefersReducedMotion();
  const docs = images.slice(0, 3);
  const on = (hoveredProp ?? hovered) && !reduced;

  const w = folderSize;
  const h = folderSize * 0.72;

  const content = (
    <div
      className={cn("relative flex flex-col items-center", className)}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      onFocus={() => setHovered(true)}
      onBlur={() => setHovered(false)}
      onTouchStart={() => setHovered((v) => !v)}
    >
      <div className="relative" style={{ width: w, height: h }}>
        {/* folder back */}
        <div
          className="absolute inset-x-0 bottom-0 rounded-[6px] rounded-tl-none border border-border-strong/70 bg-secondary/80 transition-colors duration-300 group-hover:bg-secondary"
          style={{ height: h }}
        />
        <div
          className="absolute top-0 left-0 rounded-t-[4px] border border-b-0 border-border-strong/70 bg-secondary/80"
          style={{ width: w * 0.42, height: h * 0.16 }}
        />

        {/* filing previews */}
        {docs.map((doc, i) => {
          const mid = (docs.length - 1) / 2;
          const offset = i - mid;
          const size = on ? hoverImageSize : teaserImageSize;
          return (
            <motion.div
              key={i}
              className="absolute bottom-[52%] left-1/2 origin-bottom overflow-hidden rounded-[3px] border border-border bg-background shadow-sm"
              style={{ zIndex: 10 + i, width: size, height: size * 1.28 }}
              animate={{
                x: (on ? offset * hoverSpread : offset * 5) - size / 2,
                y: on ? -hoverTranslateY : h * 0.34,
                rotate: on ? offset * hoverRotation : offset * 2.5,
                width: size,
                height: size * 1.28,
              }}
              transition={reduced ? { duration: 0 } : spring}
            >
              {doc}
            </motion.div>
          );
        })}

        {/* folder front */}
        <motion.div
          className="absolute inset-x-0 bottom-0 rounded-[6px] border border-border-strong bg-muted/90"
          style={{ height: h * 0.82, zIndex: 20, transformOrigin: "bottom center", transformPerspective: 640 }}
          animate={{ rotateX: on ? -34 : 0 }}
          transition={reduced ? { duration: 0 } : spring}
        >
          <div className="mt-2 ml-3 h-px w-1/3 bg-border-strong/60" />
        </motion.div>
      </div>

      {text ? <span className="label-mono mt-3">{text}</span> : null}
    </div>
  );

  if (href) {
    return (
      <a href={href} target={target} onClick={onSelect} className="block focus-visible:outline-none">
        {content}
      </a>
    );
  }
  return content;
}
