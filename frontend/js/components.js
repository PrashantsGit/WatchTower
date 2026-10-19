/*
 * WatchTower
 * Shared application components
 *
 * Loads the common sidebar, header, and footer
 * before page-specific application logic runs.
 */


/* ============================================================
   COMPONENT CONFIGURATION
   ============================================================ */

const COMPONENTS = {

    sidebar: "../components/sidebar.html",

    header: "../components/header.html",

    footer: "../components/footer.html"

};


/* ============================================================
   LOAD COMPONENT
   ============================================================ */

async function loadComponent(
    elementId,
    componentPath
) {

    const element =
        document.getElementById(elementId);


    if (!element) {

        console.warn(
            `WatchTower: Element #${elementId} not found.`
        );

        return;

    }


    try {

        const response =
            await fetch(componentPath);


        if (!response.ok) {

            throw new Error(
                `HTTP ${response.status}`
            );

        }


        element.innerHTML =
            await response.text();


    } catch (error) {

        console.error(
            `WatchTower: Failed to load ${componentPath}`,
            error
        );

    }

}


/* ============================================================
   ACTIVE NAVIGATION
   ============================================================ */

function setActiveNavigation() {

    const currentPage =
        document.body.dataset.page;


    if (!currentPage) {
        return;
    }


    const navigationItems =
        document.querySelectorAll(
            ".navigation-item[data-page]"
        );


    navigationItems.forEach(item => {

        const isActive =
            item.dataset.page === currentPage;


        item.classList.toggle(
            "active",
            isActive
        );


        if (isActive) {

            item.setAttribute(
                "aria-current",
                "page"
            );

        } else {

            item.removeAttribute(
                "aria-current"
            );

        }

    });

}


/* ============================================================
   PAGE HEADER
   ============================================================ */

function setPageHeader() {

    const pageTitle =
        document.getElementById("page-title");


    const pageContext =
        document.getElementById("page-context");


    if (!pageTitle) {
        return;
    }


    const pageData = {

        dashboard: {

            title: "Dashboard",

            context: "Monitoring overview"

        },

        tasks: {

            title: document.body.dataset.pageTitle || "Tasks",

            context: "Manage your monitors"
        },

        history: {

            title: "History",

            context: "Monitoring activity"

        },

        settings: {

            title: "Settings",

            context: "Application configuration"

        }

    };


    const currentPage =
        document.body.dataset.page;


    const data =
        pageData[currentPage];


    if (!data) {
        return;
    }


    pageTitle.textContent =
        data.title;


    if (pageContext) {

        pageContext.textContent =
            data.context;

    }

}


/* ============================================================
   INITIALIZATION
   ============================================================ */

async function initializeComponents() {

    await Promise.all([

        loadComponent(
            "app-sidebar",
            COMPONENTS.sidebar
        ),

        loadComponent(
            "app-header",
            COMPONENTS.header
        ),

        loadComponent(
            "app-footer",
            COMPONENTS.footer
        )

    ]);

    setupSidebarControls();

    setActiveNavigation();

    setPageHeader();

}
/* ============================================================
   SIDEBAR CONTROLS
   ============================================================ */

function setupSidebarControls() {

    const sidebar = document.querySelector(".sidebar");
    const toggleButton = document.getElementById("sidebar-toggle");
    const mobileButton = document.getElementById("mobile-menu-button");

    if (!sidebar) {
        return;
    }

    const collapsedKey = "watchtower-sidebar-collapsed";

    function setCollapsed(collapsed) {
        document.body.classList.toggle(
            "sidebar-collapsed",
            collapsed
        );

        if (toggleButton) {
            toggleButton.setAttribute(
                "aria-expanded",
                String(!collapsed)
            );

            toggleButton.setAttribute(
                "aria-label",
                collapsed ? "Expand sidebar" : "Collapse sidebar"
            );

            toggleButton.title =
                collapsed ? "Expand sidebar" : "Collapse sidebar";

            toggleButton.innerHTML =
                `<span aria-hidden="true">${collapsed ? "›" : "‹"}</span>`;
        }

        try {
            localStorage.setItem(
                collapsedKey,
                String(collapsed)
            );
        } catch (error) {
            // The sidebar still works if storage is unavailable.
        }
    }

    let initiallyCollapsed = false;

    try {
        initiallyCollapsed =
            localStorage.getItem(collapsedKey) === "true";
    } catch (error) {
        // Use the expanded layout by default.
    }

    setCollapsed(initiallyCollapsed);

    if (toggleButton) {
        toggleButton.addEventListener("click", () => {
            const collapsed =
                !document.body.classList.contains("sidebar-collapsed");

            setCollapsed(collapsed);
        });
    }

    if (mobileButton) {
        mobileButton.addEventListener("click", () => {
            const isOpen =
                document.body.classList.toggle("mobile-nav-open");

            mobileButton.setAttribute(
                "aria-expanded",
                String(isOpen)
            );

            mobileButton.setAttribute(
                "aria-label",
                isOpen ? "Close navigation" : "Open navigation"
            );

            mobileButton.title =
                isOpen ? "Close navigation" : "Open navigation";
        });
    }

    sidebar.querySelectorAll(".navigation-item").forEach(item => {
        item.addEventListener("click", () => {
            document.body.classList.remove("mobile-nav-open");

            if (mobileButton) {
                mobileButton.setAttribute("aria-expanded", "false");
                mobileButton.setAttribute("aria-label", "Open navigation");
            }
        });
    });
}

/* ============================================================
   COMPONENTS READY
   ============================================================ */

/*
 * Page-specific scripts can wait for this promise:
 *
 * await window.watchTowerComponentsReady;
 *
 * This prevents Dashboard/Tasks/etc. from trying to access
 * elements inside asynchronously loaded components too early.
 */

window.watchTowerComponentsReady =
    initializeComponents();
