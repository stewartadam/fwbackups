include $(top_srcdir)/gnome-doc-utils.make
dist-hook: doc-dist-hook
DOC_MODULE = fwbackups
DOC_ENTITIES = fdl.xml gpl.xml
DOC_INCLUDES = 
DOC_FIGURES = \
              figures/backup_sets_page.png \
              figures/configure_backup_remote.png \
              figures/onetime_configuration.png \
              figures/prefs_refresh.png \
              figures/restore.png \
              figures/notification.png

DOC_LINGUAS = 

uninstall-local:
	rm -rf $(DESTDIR)$(datadir)/gnome/help/$(DOC_MODULE)/
	rm -rf $(DESTDIR)$(datadir)/omf/$(DOC_MODULE)/
