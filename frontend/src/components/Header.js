import React from 'react';
import { Link } from 'react-router-dom';

const Header = () => (
  <header>
    <nav className="navbar is-dark" role="navigation" aria-label="main navigation">
      <div className="navbar-menu">
        <div className="navbar-start">
          <Link to="/series" className="navbar-item">Series</Link>
          <Link to="/publisher" className="navbar-item">Publishers</Link>
        </div>
      </div>
    </nav>
  </header>
)

export default Header
