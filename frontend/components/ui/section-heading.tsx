type SectionHeadingProps = {
  eyebrow: string;
  title: string;
  description?: string;
};

export function SectionHeading({
  eyebrow,
  title,
  description
}: SectionHeadingProps) {
  return (
    <div className="space-y-3">
      <p className="text-xs font-semibold uppercase tracking-[0.28em] text-sage-700/75">
        {eyebrow}
      </p>
      <h2 className="font-serif-display text-3xl text-ink sm:text-4xl">
        {title}
      </h2>
      {description ? (
        <p className="max-w-2xl text-sm leading-7 text-sage-800/76 sm:text-base">
          {description}
        </p>
      ) : null}
    </div>
  );
}
