<script>
	import { onMount, getContext } from 'svelte';
	import { toast } from 'svelte-sonner';

	import dayjs from 'dayjs';
	import localizedFormat from 'dayjs/plugin/localizedFormat';
	dayjs.extend(localizedFormat);

	import { getAdminSubscriptions, updateAdminSubscription } from '$lib/apis/translations';
	import Spinner from '$lib/components/common/Spinner.svelte';
	import Badge from '$lib/components/common/Badge.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';

	const i18n = getContext('i18n');

	let subscriptions = null;
	let query = '';
	let loading = false;

	$: filteredSubscriptions = subscriptions
		? subscriptions.filter((s) => {
				const q = query.toLowerCase();
				return (
					(s.name && s.name.toLowerCase().includes(q)) ||
					(s.email && s.email.toLowerCase().includes(q))
				);
			})
		: [];

	const loadSubscriptions = async () => {
		loading = true;
		try {
			subscriptions = await getAdminSubscriptions(localStorage.token);
		} catch (e) {
			toast.error(`${e}`);
			subscriptions = [];
		}
		loading = false;
	};

	const handleTierChange = async (email, newTier) => {
		try {
			await updateAdminSubscription(localStorage.token, email, newTier);
			toast.success('Підписку оновлено');
			await loadSubscriptions();
		} catch (e) {
			toast.error(`${e}`);
		}
	};

	const getTierBadgeType = (tier) => {
		switch (tier) {
			case 'pro':
				return 'info';
			case 'plus':
				return 'success';
			default:
				return 'muted';
		}
	};

	const formatUsage = (sub) => {
		if (!sub?.documentTranslation) return '-';
		const dt = sub.documentTranslation;
		if (dt.maxLimit === null) return `${dt.used} / ∞`;
		return `${dt.used} / ${dt.maxLimit}`;
	};

	onMount(() => {
		loadSubscriptions();
	});
</script>

{#if loading || subscriptions === null}
	<div class="my-10 flex justify-center">
		<Spinner className="size-5" />
	</div>
{:else}
	<div
		class="pt-0.5 pb-1 gap-1 flex flex-col md:flex-row justify-between sticky top-0 z-10 bg-white dark:bg-gray-900"
	>
		<div class="flex md:self-center text-lg font-medium px-0.5 gap-2">
			<div class="flex-shrink-0">
				Підписки
			</div>
			<div>
				<span class="text-lg font-medium text-gray-500 dark:text-gray-300"
					>{subscriptions.length}</span
				>
			</div>
		</div>

		<div class="flex gap-1">
			<div class="flex w-full space-x-2">
				<div class="flex flex-1">
					<div class="self-center ml-1 mr-3">
						<svg
							xmlns="http://www.w3.org/2000/svg"
							viewBox="0 0 20 20"
							fill="currentColor"
							class="w-4 h-4"
						>
							<path
								fill-rule="evenodd"
								d="M9 3.5a5.5 5.5 0 100 11 5.5 5.5 0 000-11zM2 9a7 7 0 1112.452 4.391l3.328 3.329a.75.75 0 11-1.06 1.06l-3.329-3.328A7 7 0 012 9z"
								clip-rule="evenodd"
							/>
						</svg>
					</div>
					<input
						class="w-full text-sm pr-4 py-1 rounded-r-xl outline-hidden bg-transparent"
						bind:value={query}
						placeholder="Пошук за ім'ям або email"
					/>
				</div>
			</div>
		</div>
	</div>

	<div class="overflow-x-auto w-full">
		<table class="w-full text-sm text-left text-gray-500 dark:text-gray-400 table-auto">
			<thead
				class="text-xs text-gray-700 uppercase bg-transparent dark:text-gray-200 border-b-2 dark:border-gray-800"
			>
				<tr>
					<th scope="col" class="px-3 py-2">Ім'я</th>
					<th scope="col" class="px-3 py-2">Email</th>
					<th scope="col" class="px-3 py-2">Тариф</th>
					<th scope="col" class="px-3 py-2">Використання</th>
					<th scope="col" class="px-3 py-2">Дата скидання</th>
					<th scope="col" class="px-3 py-2">Дії</th>
				</tr>
			</thead>
			<tbody>
				{#each filteredSubscriptions as sub (sub.email)}
					<tr class="bg-transparent border-b dark:border-gray-850 text-xs">
						<td class="px-3 py-2.5">
							<div class="flex items-center gap-2">
								<img
									class="rounded-full w-6 h-6"
									src={sub.profile_image_url}
									alt={sub.name}
								/>
								<span class="font-medium dark:text-white">{sub.name}</span>
							</div>
						</td>
						<td class="px-3 py-2.5">{sub.email}</td>
						<td class="px-3 py-2.5">
							{#if sub.subscription?.documentTranslation}
								<Badge
									type={getTierBadgeType(sub.subscription.documentTranslation.tier)}
									content={sub.subscription.documentTranslation.tier.toUpperCase()}
								/>
							{:else}
								<Badge type="muted" content="Немає" />
							{/if}
						</td>
						<td class="px-3 py-2.5">
							{formatUsage(sub.subscription)}
						</td>
						<td class="px-3 py-2.5">
							{#if sub.subscription?.documentTranslation?.resetDate}
								<Tooltip
									content={dayjs(sub.subscription.documentTranslation.resetDate).format(
										'LLLL'
									)}
								>
									{dayjs(sub.subscription.documentTranslation.resetDate).format('DD.MM.YYYY')}
								</Tooltip>
							{:else}
								-
							{/if}
						</td>
						<td class="px-3 py-2.5">
							<select
								class="bg-transparent border border-gray-300 dark:border-gray-700 rounded px-2 py-1 text-xs dark:text-white"
								value={sub.subscription?.documentTranslation?.tier || 'standard'}
								on:change={(e) => handleTierChange(sub.email, e.target.value)}
							>
								<option value="standard">Standard</option>
								<option value="plus">Plus</option>
								<option value="pro">Pro</option>
							</select>
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>

	{#if filteredSubscriptions.length === 0}
		<div class="w-full h-full flex flex-col justify-center items-center my-16 mb-24">
			<div class="max-w-md text-center">
				<div class="text-lg font-medium mb-1">Підписок не знайдено</div>
				<div class="text-gray-500 text-center text-xs">
					Спробуйте змінити параметри пошуку.
				</div>
			</div>
		</div>
	{/if}
{/if}
