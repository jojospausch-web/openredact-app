import React from "react";
import PropTypes from "prop-types";
import "./NavBar.sass";
import {
  NavbarGroup,
  Alignment,
  NavbarHeading,
  Classes,
} from "@blueprintjs/core";
import { ReactComponent as LogoSvg } from "../logo.svg";

const NavBar = ({ settings, about, help, whitelist, templates }) => {
  return (
    <div>
      <nav className={`${Classes.NAVBAR} ${Classes.DARK}`}>
        <NavbarGroup align={Alignment.LEFT} className="branding">
          <a href="/">
            <LogoSvg className="logo" />
          </a>
          <a href="/">
            <NavbarHeading>
              OPEN<b>REDACT</b>
            </NavbarHeading>
          </a>
        </NavbarGroup>
        <NavbarGroup align={Alignment.RIGHT}>
          {whitelist}
          {templates}
          {settings}
          {about}
          {help}
        </NavbarGroup>
      </nav>
    </div>
  );
};

NavBar.propTypes = {
  settings: PropTypes.element.isRequired,
  about: PropTypes.element.isRequired,
  help: PropTypes.element.isRequired,
  whitelist: PropTypes.element,
  templates: PropTypes.element,
};

export default NavBar;
