import "./TeamLink.css";
import { Link } from "react-router";

interface TeamLinkProps {
  id: string;
  name: string;
  shortName?: string;
  showLogo?: boolean;
}

function TeamLink({
  id,
  name,
  shortName,
  showLogo = false,
}: TeamLinkProps) {
  return (
    <Link
      to={`/teams/${id}`}
      className="team-link"
    >
      {showLogo && (
        <div className="team-link-logo">
          {shortName}
        </div>
      )}

      <span>{name}</span>
    </Link>
  );
}

export default TeamLink;