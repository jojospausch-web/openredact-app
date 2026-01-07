import React, { useState, useEffect, useContext } from "react";
import {
  Button,
  Dialog,
  Classes,
  InputGroup,
  Tag,
  Intent,
  Icon,
} from "@blueprintjs/core";
import PropTypes from "prop-types";
import "./WhitelistManager.sass";
import PolyglotContext from "../../js/polyglotContext";
import AppToaster from "../../js/toaster";
import {
  getWhitelist,
  addWhitelistEntry,
  removeWhitelistEntry,
} from "../../api/routes";

const WhitelistManager = ({ isOpen, onClose }) => {
  const t = useContext(PolyglotContext);
  const [entries, setEntries] = useState([]);
  const [newEntry, setNewEntry] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadWhitelist();
    }
  }, [isOpen]);

  const loadWhitelist = () => {
    setIsLoading(true);
    getWhitelist()
      .then((response) => {
        setEntries(response.data.entries || []);
        setIsLoading(false);
      })
      .catch(() => {
        AppToaster.show({
          message: t("whitelist.load_failed_toast") || "Failed to load whitelist",
          intent: "danger",
        });
        setIsLoading(false);
      });
  };

  const handleAddEntry = () => {
    const trimmedEntry = newEntry.trim();
    if (!trimmedEntry) {
      AppToaster.show({
        message: t("whitelist.empty_entry_error") || "Entry cannot be empty",
        intent: "warning",
      });
      return;
    }

    if (entries.includes(trimmedEntry)) {
      AppToaster.show({
        message: t("whitelist.duplicate_entry_error") || "Entry already exists",
        intent: "warning",
      });
      return;
    }

    addWhitelistEntry(trimmedEntry)
      .then(() => {
        setEntries([...entries, trimmedEntry]);
        setNewEntry("");
        AppToaster.show({
          message: t("whitelist.add_success_toast") || "Entry added successfully",
          intent: "success",
        });
      })
      .catch(() => {
        AppToaster.show({
          message: t("whitelist.add_failed_toast") || "Failed to add entry",
          intent: "danger",
        });
      });
  };

  const handleRemoveEntry = (entry) => {
    removeWhitelistEntry(entry)
      .then(() => {
        setEntries(entries.filter((e) => e !== entry));
        AppToaster.show({
          message: t("whitelist.remove_success_toast") || "Entry removed successfully",
          intent: "success",
        });
      })
      .catch(() => {
        AppToaster.show({
          message: t("whitelist.remove_failed_toast") || "Failed to remove entry",
          intent: "danger",
        });
      });
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      handleAddEntry();
    }
  };

  return (
    <Dialog
      isOpen={isOpen}
      onClose={onClose}
      title={t("whitelist.title") || "Whitelist Manager"}
      className="whitelist-dialog"
    >
      <div className={Classes.DIALOG_BODY}>
        <p className="whitelist-description">
          {t("whitelist.description") ||
            "Whitelisted terms will be excluded from anonymization. Add terms that should not be redacted (e.g., common medical terms, institution names)."}
        </p>

        <div className="whitelist-add-section">
          <InputGroup
            placeholder={t("whitelist.add_placeholder") || "Enter term to whitelist..."}
            value={newEntry}
            onChange={(e) => setNewEntry(e.target.value)}
            onKeyPress={handleKeyPress}
            rightElement={
              <Button
                icon="add"
                minimal
                onClick={handleAddEntry}
                disabled={!newEntry.trim()}
              />
            }
          />
        </div>

        <div className="whitelist-entries">
          {isLoading && <p>Loading...</p>}
          {!isLoading && entries.length === 0 && (
            <p className="no-entries">
              {t("whitelist.no_entries") || "No whitelist entries yet."}
            </p>
          )}
          {!isLoading &&
            entries.map((entry) => (
              <Tag
                key={entry}
                large
                onRemove={() => handleRemoveEntry(entry)}
                className="whitelist-tag"
              >
                {entry}
              </Tag>
            ))}
        </div>
      </div>
      <div className={Classes.DIALOG_FOOTER}>
        <div className={Classes.DIALOG_FOOTER_ACTIONS}>
          <Button onClick={onClose}>{t("common.close") || "Close"}</Button>
        </div>
      </div>
    </Dialog>
  );
};

WhitelistManager.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
};

export default WhitelistManager;
