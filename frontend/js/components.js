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

            title: "Tasks",

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


    setActiveNavigation();

    setPageHeader();

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