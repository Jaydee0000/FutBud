import {
  Link as RouterLink,
} from "react-router";

import "./TeamLink.css";


interface TeamLinkProps {
  teamId: number;

  name: string;

  logoUrl?: string | null;

  className?: string;

  showLogo?: boolean;
}


function TeamLink({
  teamId,
  name,
  logoUrl,
  className = "",
  showLogo = true,
}: TeamLinkProps) {

  return (
    <RouterLink
      to={`/teams/${teamId}`}
      className={
        `team-link ${className}`
      }
    >

      {showLogo && logoUrl && (

        <img
          src={logoUrl}
          alt=""
          className="team-link-logo"
        />

      )}


      <span>
        {name}
      </span>

    </RouterLink>
  );
}


export default TeamLink;