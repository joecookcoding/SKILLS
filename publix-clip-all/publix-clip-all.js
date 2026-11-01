(async () => {
  const sleep = ms => new Promise(r => setTimeout(r, ms));

  const BATCH_SIZE = 10;
  const BATCH_DELAY_MS = 1400;
  const LOAD_MORE_TIMEOUT_MS = 15000;

  const getClipButtons = () =>
    [...document.querySelectorAll('button')]
      .filter(b =>
        b.innerText.trim().toLowerCase() === 'clip coupon' &&
        !b.disabled
      );

  const getLoadMore = () =>
    document.querySelector(
      'button[data-qa-automation="button-Load more"]'
    );

  let totalClipped = 0;
  let loadMoreClicks = 0;

  console.log("🚀 Starting Publix clip-all...");

  while (true) {
    while (true) {
      const buttons = getClipButtons();

      if (!buttons.length) break;

      const batch = buttons.slice(0, BATCH_SIZE);

      batch.forEach(button => {
        if (button.isConnected && !button.disabled) {
          button.click();
          totalClipped++;
        }
      });

      console.log(
        `✂️ Clicked ${batch.length} coupons — ${totalClipped} total`
      );

      await sleep(BATCH_DELAY_MS);
    }

    const loadMore = getLoadMore();

    if (!loadMore || loadMore.disabled) {
      console.log("🏁 No more Load More button.");
      break;
    }

    loadMore.scrollIntoView({
      block: "center",
      behavior: "auto"
    });

    await sleep(400);

    const beforeHeight = document.documentElement.scrollHeight;
    const beforeButtons = document.querySelectorAll("button").length;

    console.log("⬇️ Clicking Load More...");

    HTMLElement.prototype.click.call(loadMore);
    loadMoreClicks++;

    let changed = false;
    const checks = Math.ceil(LOAD_MORE_TIMEOUT_MS / 500);

    for (let i = 0; i < checks; i++) {
      await sleep(500);

      const afterHeight = document.documentElement.scrollHeight;
      const afterButtons = document.querySelectorAll("button").length;

      if (
        afterHeight > beforeHeight ||
        afterButtons > beforeButtons ||
        getClipButtons().length > 0
      ) {
        changed = true;
        console.log(
          `✅ New coupons loaded — Load More #${loadMoreClicks}`
        );
        break;
      }
    }

    if (!changed) {
      console.warn(
        "⚠️ Load More was clicked, but no new coupons appeared."
      );
      break;
    }

    await sleep(800);
  }

  console.log(
    `✅ DONE — clicked ${totalClipped} coupons and used Load More ${loadMoreClicks} times.`
  );
})();
