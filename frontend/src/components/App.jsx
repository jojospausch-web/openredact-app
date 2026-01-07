import React, { useContext, useEffect, useState } from "react";
import "./App.sass";
import NavBar from "./NavBar";
import AnonymizationConfigMenu from "./anonymizationConfig/AnonymizationConfigMenu";
import Main from "./Main";
import PolyglotContext from "../js/polyglotContext";
import { fetchRecognizers, fetchTags } from "../api/routes";
import AppToaster from "../js/toaster";
import useLocalStorage from "../js/useLocalStorage";
import ErrorBoundary from "./ErrorBoundary";
import Settings from "./Settings";
import About from "./About";
import Help from "./Help";
import WhitelistManager from "./whitelist/WhitelistManager";
import TemplateManager from "./templates/TemplateManager";
import { Button } from "@blueprintjs/core";

const App = () => {
  const t = useContext(PolyglotContext);

  const [tags, setTags] = useState([]);
  const [availableRecognizers, setAvailableRecognizers] = useState([]);
  const [activatedRecognizers, setActivatedRecognizers] = useLocalStorage(
    "activatedRecognizers",
    null
  );
  const [anonymizationConfig, setAnonymizationConfig] = useLocalStorage(
    "anonymizationConfig",
    {
      defaultMechanism: {
        mechanism: "suppression",
        config: { suppressionChar: "X" },
      },
      mechanismsByTag: {},
    }
  );
  const [showWhitelist, setShowWhitelist] = useState(false);
  const [showTemplates, setShowTemplates] = useState(false);

  useEffect(() => {
    fetchRecognizers()
      .then((response) => {
        setAvailableRecognizers(response.data);
        if (activatedRecognizers === null)
          setActivatedRecognizers(response.data);
      })
      .catch(() => {
        AppToaster.show({
          message: t("app.fetching_recognizers_failed_toast"),
          intent: "danger",
        });
      });
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    fetchTags()
      .then((response) => {
        setTags(response.data);
      })
      .catch(() => {
        AppToaster.show({
          message: t("annotation.fetching_tags_failed_toast"),
          intent: "danger",
        });
      });
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div>
      <NavBar
        settings={
          <Settings
            setActivatedRecognizers={setActivatedRecognizers}
            availableRecognizers={availableRecognizers}
            activatedRecognizers={activatedRecognizers || []}
          />
        }
        about={<About />}
        help={<Help />}
        whitelist={
          <Button
            icon="filter-list"
            title={t("nav.whitelist") || "Whitelist"}
            minimal
            onClick={() => setShowWhitelist(true)}
          />
        }
        templates={
          <Button
            icon="document"
            title={t("nav.templates") || "Templates"}
            minimal
            onClick={() => setShowTemplates(true)}
          />
        }
      />
      <div className="grid-container">
        <ErrorBoundary>
          <AnonymizationConfigMenu
            tags={tags}
            config={anonymizationConfig}
            setConfig={setAnonymizationConfig}
          />
        </ErrorBoundary>
        <ErrorBoundary>
          <Main
            tags={tags}
            anonymizationConfig={anonymizationConfig}
            activatedRecognizers={activatedRecognizers || []}
          />
        </ErrorBoundary>
      </div>
      <WhitelistManager
        isOpen={showWhitelist}
        onClose={() => setShowWhitelist(false)}
      />
      <TemplateManager
        isOpen={showTemplates}
        onClose={() => setShowTemplates(false)}
        currentConfig={anonymizationConfig}
        onApplyTemplate={setAnonymizationConfig}
      />
    </div>
  );
};

export default App;
