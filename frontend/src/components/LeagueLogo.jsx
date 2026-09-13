import { useState } from 'react';

/**
 * League badge on a tile (white unless the league's badge needs a dark one), or the league
 * code on the league colour when there is no logo or it fails to load. Decorative — the
 * league name is always shown next to it.
 */
export function LeagueLogo({ league, size = 'sm' }) {
  const [failedLogo, setFailedLogo] = useState(null);
  const showImage = league.logo && league.logo !== failedLogo;

  return (
    <span
      className={`league-logo league-logo--${size}${showImage ? '' : ' league-logo--fallback'}`}
      style={{ '--chip': league.color, '--tile': league.logoBackground }}
      aria-hidden="true"
    >
      {showImage ? (
        <img src={league.logo} alt="" loading="lazy" decoding="async" onError={() => setFailedLogo(league.logo)} />
      ) : (
        league.code
      )}
    </span>
  );
}
