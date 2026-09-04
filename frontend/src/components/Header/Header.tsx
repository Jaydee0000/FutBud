import "./Header.css";

import { useState } from "react";
import { NavLink } from "react-router";

function Header() {
  const [menuOpen, setMenuOpen] = useState(false);

  function closeMenu() {
    setMenuOpen(false);
  }

  return (
    <header className="header">
      <div className="header-inner">

        <NavLink
          to="/"
          className="logo"
          onClick={closeMenu}
        >
          FUTBUD
        </NavLink>

        <nav className={`header-nav ${menuOpen ? "open" : ""}`}>
          <NavLink to="/" onClick={closeMenu}>
            Home
          </NavLink>

          <NavLink to="/players" onClick={closeMenu}>
            Players
          </NavLink>

          <NavLink to="/teams" onClick={closeMenu}>
            Teams
          </NavLink>

          <NavLink to="/leagues" onClick={closeMenu}>
            Leagues
          </NavLink>

          <NavLink to="/matches" onClick={closeMenu}>
            Matches
          </NavLink>

          <NavLink to="/rankings" onClick={closeMenu}>
            Rankings
          </NavLink>
        </nav>

        <div className="header-search">
          <input
            type="text"
            placeholder="Search players, teams..."
          />

          <button type="button">
            Search
          </button>
        </div>

        <button
          className="menu-button"
          type="button"
          aria-label="Toggle navigation menu"
          aria-expanded={menuOpen}
          onClick={() => setMenuOpen((open) => !open)}
        >
          ☰
        </button>

      </div>
    </header>
  );
}

export default Header;