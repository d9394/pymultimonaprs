include $(TOPDIR)/rules.mk

PKG_NAME:=pymultimonaprs
PKG_VERSION:=1.0.0
PKG_RELEASE:=1

PKG_SOURCE_PROTO:=git
PKG_SOURCE_URL:=https://github.com/d9394/pymultimonaprs.git
PKG_SOURCE_SUBDIR:=$(PKG_NAME)-$(PKG_VERSION)
PKG_SOURCE_VERSION:=openwrt
PKG_SOURCE:=$(PKG_NAME)-$(PKG_VERSION)-$(PKG_SOURCE_VERSION).tar.gz

PKG_MAINTAINER:=d9394
#PKG_BUILD_DIR:=$(BUILD_DIR)/$(PKG_NAME)/$(BUILD_VARIANT)/$(PKG_NAME)-$(PKG_VERSION)
PKG_BUILD_DIR:=$(BUILD_DIR)/$(PKG_SOURCE_SUBDIR)

include $(INCLUDE_DIR)/package.mk

define Package/pymultimonaprs/Default
  TITLE:=pymultimonaprs is a python tools to received aprs packet from RTL-SDR and decode, then send it to aprs network, sometimes we also call this : IGate.
  URL:=https://github.com/d9394/pymultimonaprs
endef

define Build/Prepare
#	mkdir -p $(PKG_BUILD_DIR)
#	$(CP) /home/openwrt/pymultimonaprs/* $(PKG_BUILD_DIR)/
	$(call Build/Prepare/Default)
endef

define Package/pymultimonaprs
  $(call Package/pymultimonaprs/Default)
  SECTION:=utils
  CATEGORY:=Utilities
  DEPENDS:=+:multimon-ng +python-light +python-codecs +python-logging +python-openssl
endef

define Package/pymultimonaprs/description
  pymultimonaprs is a python tools to received aprs packet from RTL-SDR and decode, then send it to aprs network, sometimes we also call this : IGate.
endef

define Build/Compile
endef

define Package/pymultimonaprs/install
	$(INSTALL_DIR) $(1)/etc/$(PKG_NAME)
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/files/*.py $(1)/etc/$(PKG_NAME)/
	$(INSTALL_DATA) $(PKG_BUILD_DIR)/files/$(PKG_NAME).config $(1)/etc/config/$(PKG_NAME)
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/pymultimonaprs.init $(1)/etc/init.d/$(PKG_NAME)
endef

$(eval $(call BuildPackage,pymultimonaprs))
