<script lang="ts">
	import dayjs from 'dayjs';
	import relativeTime from 'dayjs/plugin/relativeTime';
	import localizedFormat from 'dayjs/plugin/localizedFormat';
	import 'dayjs/locale/uk';
	dayjs.extend(relativeTime);
	dayjs.extend(localizedFormat);
	dayjs.locale('uk');

	import { toast } from 'svelte-sonner';
	import { onMount, getContext } from 'svelte';
	const i18n = getContext('i18n');

	import { WEBUI_NAME, user } from '$lib/stores';
	import { getMyTranslationHistory, getMySubscription } from '$lib/apis/translations';

	import Badge from '../common/Badge.svelte';
	import Search from '../icons/Search.svelte';
	import Spinner from '../common/Spinner.svelte';
	import Tooltip from '../common/Tooltip.svelte';
	import XMark from '../icons/XMark.svelte';
	import Loader from '../common/Loader.svelte';

	let loaded = false;

	let items = null;
	let total = null;
	let page = 1;
	const PAGE_SIZE = 20;

	let query = '';
	let dateFrom = '';
	let dateTo = '';

	let allItemsLoaded = false;
	let itemsLoading = false;

	let subscription = null;

	$: filteredItems = items
		? items.filter((item) => {
				let match = true;
				if (query) {
					const q = query.toLowerCase();
					match =
						(item.original_filename && item.original_filename.toLowerCase().includes(q)) ||
						(item.translated_filename && item.translated_filename.toLowerCase().includes(q));
				}
				if (match && dateFrom) {
					match = dayjs(item.created_at).isAfter(dayjs(dateFrom).startOf('day'));
				}
				if (match && dateTo) {
					match = dayjs(item.created_at).isBefore(dayjs(dateTo).endOf('day'));
				}
				return match;
			})
		: [];

	const loadMoreItems = async () => {
		if (allItemsLoaded || itemsLoading) return;
		page += 1;
		await loadPage();
	};

	const loadPage = async () => {
		itemsLoading = true;
		try {
			const offset = (page - 1) * PAGE_SIZE;
			const res = await getMyTranslationHistory(localStorage.token, PAGE_SIZE, offset);
			if (res) {
				total = res.total || 0;
				const pageItems = res.history || [];
				if (pageItems.length === 0 || pageItems.length < PAGE_SIZE) {
					allItemsLoaded = true;
				}
				if (items) {
					items = [...items, ...pageItems];
				} else {
					items = pageItems;
				}
			}
		} catch (e) {
			toast.error(`${e}`);
		}
		itemsLoading = false;
	};

	const init = async () => {
		page = 1;
		items = null;
		total = null;
		allItemsLoaded = false;
		await loadPage();
	};

	const formatFileSize = (bytes) => {
		if (!bytes) return '-';
		if (bytes < 1024) return `${bytes} Б`;
		if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} КБ`;
		return `${(bytes / (1024 * 1024)).toFixed(1)} МБ`;
	};

	const getStatusBadgeType = (status) => {
		switch (status) {
			case 'completed':
				return 'success';
			case 'error':
				return 'error';
			case 'processing':
				return 'info';
			default:
				return 'muted';
		}
	};

	const getStatusLabel = (status) => {
		switch (status) {
			case 'completed':
				return 'Завершено';
			case 'error':
				return 'Помилка';
			case 'processing':
				return 'Обробка';
			default:
				return status;
		}
	};

	const getSubscriptionText = () => {
		if (!subscription?.documentTranslation) return '';
		const dt = subscription.documentTranslation;
		const usage = dt.maxLimit === null ? `${dt.used} / ∞` : `${dt.used} / ${dt.maxLimit}`;
		return `${dt.tier.toUpperCase()} | ${usage}`;
	};

	onMount(async () => {
		try {
			subscription = await getMySubscription(localStorage.token);
		} catch (e) {
			// Підписка може бути недоступна
		}
		await init();
		loaded = true;
	});
</script>

<svelte:head>
	<title>
		Мої переклади | {$WEBUI_NAME}
	</title>
</svelte:head>

{#if loaded}
	<div class="flex flex-col gap-1 px-1 mt-1.5 mb-3">
		<div class="flex justify-between items-center">
			<div class="flex items-center md:self-center text-xl font-medium px-0.5 gap-2 shrink-0">
				<div>
					Мої переклади
				</div>
				<div class="text-lg font-medium text-gray-500 dark:text-gray-500">
					{total ?? 0}
				</div>
			</div>

			{#if subscription?.documentTranslation}
				<div
					class="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-gray-50 dark:bg-gray-850 text-xs"
				>
					<Badge
						type={subscription.documentTranslation.tier === 'pro'
							? 'info'
							: subscription.documentTranslation.tier === 'plus'
								? 'success'
								: 'muted'}
						content={subscription.documentTranslation.tier.toUpperCase()}
					/>
					<span class="text-gray-500">
						{getSubscriptionText()}
					</span>
					{#if subscription.documentTranslation.resetDate}
						<Tooltip
							content={`Скидання: ${dayjs(subscription.documentTranslation.resetDate).format('DD.MM.YYYY')}`}
						>
							<svg
								xmlns="http://www.w3.org/2000/svg"
								viewBox="0 0 16 16"
								fill="currentColor"
								class="size-3 text-gray-400"
							>
								<path
									fill-rule="evenodd"
									d="M8 15A7 7 0 1 0 8 1a7 7 0 0 0 0 14Zm.75-10.25a.75.75 0 0 0-1.5 0v3.5c0 .199.079.39.22.53l2 2a.75.75 0 1 0 1.06-1.06l-1.78-1.78V4.75Z"
									clip-rule="evenodd"
								/>
							</svg>
						</Tooltip>
					{/if}
				</div>
			{/if}
		</div>
	</div>

	<div
		class="py-2 bg-white dark:bg-gray-900 rounded-3xl border border-gray-100/30 dark:border-gray-850/30"
	>
		<div class="flex w-full space-x-2 py-0.5 px-3.5 pb-2">
			<div class="flex flex-1">
				<div class="self-center ml-1 mr-3">
					<Search className="size-3.5" />
				</div>
				<input
					class="w-full text-sm py-1 rounded-r-xl outline-hidden bg-transparent"
					bind:value={query}
					placeholder="Пошук за назвою файлу"
				/>
				{#if query}
					<div class="self-center pl-1.5 translate-y-[0.5px] rounded-l-xl bg-transparent">
						<button
							class="p-0.5 rounded-full hover:bg-gray-100 dark:hover:bg-gray-900 transition"
							on:click={() => {
								query = '';
							}}
						>
							<XMark className="size-3" strokeWidth="2" />
						</button>
					</div>
				{/if}
			</div>
			<div class="flex items-center gap-2 text-xs">
				<input
					type="date"
					class="bg-transparent border border-gray-200 dark:border-gray-700 rounded px-2 py-1 text-xs"
					bind:value={dateFrom}
					placeholder="Від"
				/>
				<span class="text-gray-400">-</span>
				<input
					type="date"
					class="bg-transparent border border-gray-200 dark:border-gray-700 rounded px-2 py-1 text-xs"
					bind:value={dateTo}
					placeholder="До"
				/>
			</div>
		</div>

		{#if items !== null && total !== null}
			{#if filteredItems.length !== 0}
				<div class="my-2 px-3 grid grid-cols-1 lg:grid-cols-2 gap-2">
					{#each filteredItems as item}
						<div
							class="flex flex-col w-full px-3 py-2.5 dark:hover:bg-gray-850/50 hover:bg-gray-50 transition rounded-2xl border border-gray-100 dark:border-gray-800"
						>
							<div class="flex items-center justify-between mb-1.5">
								<div class="flex items-center gap-2">
									<Badge
										type={getStatusBadgeType(item.status)}
										content={getStatusLabel(item.status)}
									/>
									{#if item.detected_source_lang && item.target_lang}
										<span class="text-xs text-gray-500">
											{item.detected_source_lang} → {item.target_lang}
										</span>
									{/if}
								</div>
								<Tooltip content={dayjs(item.created_at).format('LLLL')}>
									<span class="text-xs text-gray-400">
										{dayjs(item.created_at).fromNow()}
									</span>
								</Tooltip>
							</div>

							<div class="flex items-center gap-1.5 mb-1">
								<svg
									xmlns="http://www.w3.org/2000/svg"
									viewBox="0 0 16 16"
									fill="currentColor"
									class="size-3.5 text-gray-400 shrink-0"
								>
									<path
										d="M3.5 3.75a.75.75 0 0 0-1.5 0v8.5c0 .414.336.75.75.75h8.5a.75.75 0 0 0 0-1.5H3.5V3.75Z"
									/>
									<path
										d="M6 6.5a.75.75 0 0 1 .75-.75h6.5a.75.75 0 0 1 .75.75v6.5a.75.75 0 0 1-.75.75h-6.5A.75.75 0 0 1 6 13V6.5Z"
									/>
								</svg>
								<span class="text-sm font-medium line-clamp-1 dark:text-white">
									{item.original_filename}
								</span>
								<span class="text-xs text-gray-400 shrink-0">
									({formatFileSize(item.original_size)})
								</span>
							</div>

							{#if item.status === 'completed' && item.translated_filename}
								<div class="flex items-center gap-1.5 mb-2">
									<svg
										xmlns="http://www.w3.org/2000/svg"
										viewBox="0 0 16 16"
										fill="currentColor"
										class="size-3.5 text-green-500 shrink-0"
									>
										<path
											fill-rule="evenodd"
											d="M12.416 3.376a.75.75 0 0 1 .208 1.04l-5 7.5a.75.75 0 0 1-1.154.114l-3-3a.75.75 0 0 1 1.06-1.06l2.353 2.353 4.493-6.74a.75.75 0 0 1 1.04-.207Z"
											clip-rule="evenodd"
										/>
									</svg>
									<span class="text-sm line-clamp-1 text-green-600 dark:text-green-400">
										{item.translated_filename}
									</span>
								</div>
							{/if}

							<div class="flex items-center gap-2 mt-auto">
								{#if item.original_url}
									<a
										href={item.original_url}
										target="_blank"
										rel="noopener noreferrer"
										class="text-xs px-2 py-1 rounded-lg bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition"
									>
										Оригінал
									</a>
								{/if}
								{#if item.translated_url}
									<a
										href={item.translated_url}
										target="_blank"
										rel="noopener noreferrer"
										class="text-xs px-2 py-1 rounded-lg bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 hover:bg-blue-100 dark:hover:bg-blue-900/50 transition"
									>
										Завантажити переклад
									</a>
								{/if}
								{#if item.billed_characters}
									<span class="text-xs text-gray-400 ml-auto">
										{item.billed_characters.toLocaleString()} симв.
									</span>
								{/if}
							</div>
						</div>
					{/each}
				</div>

				{#if !allItemsLoaded}
					<Loader
						on:visible={() => {
							if (!itemsLoading) {
								loadMoreItems();
							}
						}}
					>
						<div class="w-full flex justify-center py-4 text-xs animate-pulse items-center gap-2">
							<Spinner className="size-4" />
							<div>Завантаження...</div>
						</div>
					</Loader>
				{/if}
			{:else}
				<div class="w-full h-full flex flex-col justify-center items-center my-16 mb-24">
					<div class="max-w-md text-center">
						<div class="text-3xl mb-3">📄</div>
						<div class="text-lg font-medium mb-1">
							Перекладів не знайдено
						</div>
						<div class="text-gray-500 text-center text-xs">
							Ваші перекладені документи з'являться тут.
						</div>
					</div>
				</div>
			{/if}
		{:else}
			<div class="w-full h-full flex justify-center items-center py-10">
				<Spinner className="size-4" />
			</div>
		{/if}
	</div>
{:else}
	<div class="w-full h-full flex justify-center items-center">
		<Spinner className="size-5" />
	</div>
{/if}
