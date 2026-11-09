<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:sm="http://www.sitemaps.org/schemas/sitemap/0.9"
  exclude-result-prefixes="sm">
  <xsl:output method="html" version="4.0" encoding="UTF-8" indent="yes"/>
  <xsl:variable name="urls" select="/sm:urlset/sm:url"/>

  <xsl:template name="url-row">
    <li class="url-row">
      <a href="{sm:loc}" target="_self">
        <xsl:choose>
          <xsl:when test="sm:loc='https://playspotstore.online/'">/ (Pagina principală)</xsl:when>
          <xsl:otherwise><xsl:value-of select="substring-after(sm:loc,'https://playspotstore.online/')"/></xsl:otherwise>
        </xsl:choose>
      </a>
      <xsl:choose>
        <xsl:when test="contains(sm:loc,'/ru/') or contains(sm:loc,'/ru.html')"><span class="language">RU</span></xsl:when>
        <xsl:otherwise><span class="language">RO</span></xsl:otherwise>
      </xsl:choose>
    </li>
  </xsl:template>

  <xsl:template name="product-group">
    <xsl:param name="category"/>
    <xsl:param name="heading"/>
    <xsl:variable name="items" select="$urls[contains(sm:loc,concat('/produse/',$category,'/'))]"/>
    <details class="group">
      <summary>
        <span class="summary-heading"><span class="dot"></span><xsl:value-of select="$heading"/></span>
        <span class="count"><xsl:value-of select="count($items)"/> URL-uri</span>
      </summary>
      <ul class="url-list"><xsl:for-each select="$items"><xsl:call-template name="url-row"/></xsl:for-each></ul>
    </details>
  </xsl:template>

  <xsl:template match="/">
    <html lang="ro">
      <head>
        <meta charset="UTF-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1"/>
        <title>Sitemap XML · PlaySpotStore</title>
        <style type="text/css">
          *{box-sizing:border-box}
          html{color-scheme:dark;font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif}
          body{min-height:100vh;margin:0;color:#e6fff3;background:radial-gradient(ellipse 60% 36% at 17% 2%,rgba(13,118,93,.24),transparent),linear-gradient(130deg,#061c20 0%,#091826 70%,#10152b 100%)}
          header{padding:35px clamp(18px,4vw,60px) 32px;border-bottom:1px solid rgba(96,250,190,.24);background:rgba(5,25,27,.55)}
          .wrap{max-width:1250px;margin:0 auto}
          .brand{display:inline-flex;gap:12px;align-items:center;color:#87ffcf;font-weight:800;font-size:13px;letter-spacing:.1em;text-transform:uppercase}
          .brand .mark{height:27px;width:27px;border-radius:9px;background:linear-gradient(120deg,#53f5b2,#78dbf3);display:inline-grid;place-items:center;color:#05392a;font-size:16px}
          h1{font-size:clamp(29px,4.5vw,49px);letter-spacing:-.045em;line-height:1.1;margin:22px 0 10px}
          .intro{color:#adcec4;font-size:15px;max-width:760px;line-height:1.65}
          .stats{display:flex;flex-wrap:wrap;gap:12px;margin:28px 0 0}
          .stat{border:1px solid rgba(103,255,195,.23);background:rgba(30,101,82,.16);border-radius:12px;padding:12px 18px;min-width:132px}
          .stat strong{display:block;font-size:23px;color:#9affcf;font-variant-numeric:tabular-nums}
          .stat span{color:#b4dbd0;font-size:12px}
          main{padding:34px clamp(18px,4vw,60px) 80px}
          .bar{display:flex;align-items:flex-end;justify-content:space-between;gap:12px;flex-wrap:wrap;margin:0 0 19px}
          h2{font-size:22px;margin:0;letter-spacing:-.025em}
          .hint{font-size:12px;color:#95c4b6;line-height:1.5}
          .group{border:1px solid rgba(109,238,190,.22);background:linear-gradient(115deg,rgba(15,50,51,.86),rgba(9,24,42,.94));border-radius:14px;overflow:hidden;margin-bottom:12px;box-shadow:0 10px 35px rgba(0,0,0,.1)}
          .group summary{cursor:pointer;display:flex;align-items:center;justify-content:space-between;gap:12px;list-style:none;min-height:67px;padding:16px 20px;font-weight:750;color:#e3fff4}
          .group summary::-webkit-details-marker{display:none}
          .group summary:after{content:'⌄';font-size:21px;color:#84ffcf;transition:transform .18s}
          .group[open] summary:after{transform:rotate(180deg)}
          .group summary:hover{background:rgba(77,211,154,.08)}
          .summary-heading{display:inline-flex;align-items:center;gap:12px;flex:1;font-size:15px}
          .dot{display:inline-block;width:9px;height:9px;border-radius:50%;background:#71ffd0;box-shadow:0 0 14px rgba(81,255,186,.6)}
          .count{border:1px solid rgba(108,239,186,.2);color:#9ae6c9;font-size:12px;padding:5px 10px;border-radius:100px;white-space:nowrap;font-weight:650}
          .url-list{list-style:none;margin:0;padding:8px 20px 18px;border-top:1px solid rgba(109,238,190,.12)}
          .url-row{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:10px 0;border-bottom:1px solid rgba(104,201,168,.09)}
          .url-row:last-child{border-bottom:0}
          .url-row a{font-size:13px;color:#beecdf;text-decoration:none;overflow-wrap:anywhere;min-width:0;line-height:1.5}
          .url-row a:hover{text-decoration:underline;color:#89ffcb}
          .language{font-size:10px;flex:0 0 auto;color:#a1d5c3;background:rgba(89,207,166,.12);border:1px solid rgba(106,246,184,.2);border-radius:5px;padding:3px 6px}
          .note{font-size:13px;color:#a0c3b8;margin-top:20px;line-height:1.7}
          .note a{color:#93ffd2;text-decoration:underline;text-underline-offset:3px}
          @media(max-width:600px){header{padding-top:27px}main{padding-top:25px}.stats{gap:8px}.stat{min-width:0;flex:1 1 96px;padding:10px 12px}.stat strong{font-size:21px}.group summary{padding:14px 12px}.url-list{padding:6px 12px 12px}.summary-heading{font-size:13px}.url-row a{font-size:12px}}
        </style>
      </head>
      <body>
        <header><div class="wrap">
          <div class="brand"><span class="mark">P</span> PlaySpotStore · SEO</div>
          <h1>XML Sitemap</h1>
          <p class="intro">Toate paginile PlaySpotStore din sitemap-ul oficial. Acest design este doar pentru afișare în browser; Google citește în continuare fișierul XML original.</p>
          <div class="stats">
            <div class="stat"><strong><xsl:value-of select="count($urls)"/></strong><span>URL-uri indexabile</span></div>
            <div class="stat"><strong><xsl:value-of select="count($urls[contains(sm:loc,'/produse/')])"/></strong><span>Pagini de produse</span></div>
            <div class="stat"><strong><xsl:value-of select="count($urls[contains(sm:loc,'/categorii/')])"/></strong><span>Pagini de categorii</span></div>
          </div>
        </div></header>
        <main><div class="wrap">
          <div class="bar"><h2>Pagini incluse</h2><span class="hint">Apasă pe o categorie ca să vezi URL-urile ei</span></div>
          <details class="group" open="open"><summary><span class="summary-heading"><span class="dot"></span>Pagini principale</span><span class="count"><xsl:value-of select="count($urls[not(contains(sm:loc,'/categorii/')) and not(contains(sm:loc,'/produse/'))])"/> URL-uri</span></summary>
            <ul class="url-list"><xsl:for-each select="$urls[not(contains(sm:loc,'/categorii/')) and not(contains(sm:loc,'/produse/'))]"><xsl:call-template name="url-row"/></xsl:for-each></ul>
          </details>
          <details class="group"><summary><span class="summary-heading"><span class="dot"></span>Pagini de categorii</span><span class="count"><xsl:value-of select="count($urls[contains(sm:loc,'/categorii/')])"/> URL-uri</span></summary>
            <ul class="url-list"><xsl:for-each select="$urls[contains(sm:loc,'/categorii/')]"><xsl:call-template name="url-row"/></xsl:for-each></ul>
          </details>
          <xsl:call-template name="product-group"><xsl:with-param name="category" select="'ps2'"/><xsl:with-param name="heading" select="'Jocuri PS2'"/></xsl:call-template>
          <xsl:call-template name="product-group"><xsl:with-param name="category" select="'ps4'"/><xsl:with-param name="heading" select="'Jocuri PS4'"/></xsl:call-template>
          <xsl:call-template name="product-group"><xsl:with-param name="category" select="'ps5'"/><xsl:with-param name="heading" select="'Jocuri PS5'"/></xsl:call-template>
          <xsl:call-template name="product-group"><xsl:with-param name="category" select="'nintendo'"/><xsl:with-param name="heading" select="'Jocuri Nintendo'"/></xsl:call-template>
          <xsl:call-template name="product-group"><xsl:with-param name="category" select="'xbox'"/><xsl:with-param name="heading" select="'Jocuri Xbox'"/></xsl:call-template>
          <xsl:call-template name="product-group"><xsl:with-param name="category" select="'console'"/><xsl:with-param name="heading" select="'Console'"/></xsl:call-template>
          <xsl:call-template name="product-group"><xsl:with-param name="category" select="'accessories'"/><xsl:with-param name="heading" select="'Accesorii'"/></xsl:call-template>
          <p class="note">Pentru Google, folosește această adresă: <a href="/sitemap.xml">https://playspotstore.online/sitemap.xml</a>. <a href="/robots.txt">robots.txt</a> rămâne conectat la același fișier.</p>
        </div></main>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
