import { useState } from 'react';
import { readableTextColor } from '../lib/color.js';

/**
 * Club logo, or the club code on its primary colour when there is no logo or it fails to load.
 * Decorative — the team name is always shown next to it.
 */
export function Crest({ crest, size = 'md' }) {
  const [failedLogo, setFailedLogo] = useState(null);

  if (crest.logo && crest.logo !== failedLogo) {
    return (
      <img
        className={`crest crest--logo crest--${size}`}
        src={crest.logo}
        alt=""
        loading="lazy"
        decoding="async"
        onError={() => setFailedLogo(crest.logo)}
      />
    );
  }

  return (
    <span
      className={`crest crest--badge crest--${size}`}
      style={{ '--crest-bg': crest.color, '--crest-fg': readableTextColor(crest.color) }}
      aria-hidden="true"
    >
      {crest.code}
    </span>
  );
}
