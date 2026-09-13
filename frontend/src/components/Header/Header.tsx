import "./Header.css";

import { useState } from "react";
import { NavLink } from "react-router";
import GlobalSearch from "../GlobalSearch/GlobalSearch";

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

          <NavLink to="/rankings" onClick={closeMenu}>
            Rankings
          </NavLink>
        </nav>

        <GlobalSearch />

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