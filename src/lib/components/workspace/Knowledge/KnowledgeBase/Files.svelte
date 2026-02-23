<script lang="ts">
	import dayjs from '$lib/dayjs';
	import duration from 'dayjs/plugin/duration';
	import relativeTime from 'dayjs/plugin/relativeTime';

	dayjs.extend(duration);
	dayjs.extend(relativeTime);

	import { getContext } from 'svelte';
	const i18n = getContext('i18n');

	import { capitalizeFirstLetter, formatFileSize } from '$lib/utils';
	import { WEBUI_API_BASE_URL } from '$lib/constants';

	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import DocumentPage from '$lib/components/icons/DocumentPage.svelte';
	import XMark from '$lib/components/icons/XMark.svelte';
	import Spinner from '$lib/components/common/Spinner.svelte';

	export let knowledge = null;
	export let selectedFileId = null;
	export let files = [];

	export let onClick = (fileId) => {};
	export let onDelete = (fileId) => {};
</script>

<div class=" max-h-full flex flex-col w-full gap-[0.5px]">
	{#each files as file (file?.id ?? file?.itemId ?? file?.tempId)}
		<div
			class=" flex cursor-pointer w-full px-1.5 py-0.5 bg-transparent dark:hover:bg-gray-850/50 hover:bg-white rounded-xl transition {selectedFileId
				? ''
				: 'hover:bg-gray-100 dark:hover:bg-gray-850'}"
		>
			<button
				class="relative group flex items-center gap-1 rounded-xl p-2 text-left flex-1 justify-between"
				type="button"
				on:click={async () => {
					console.log(file);
					onClick(file?.id ?? file?.tempId);
				}}
			>
				<div class="">
					<div class="flex gap-2 items-center line-clamp-1">
						<div class="shrink-0">
							{#if file?.status !== 'uploading'}
								<DocumentPage className="size-3.5" />
							{:else}
								<Spinner className="size-3.5" />
							{/if}
						</div>

						<div class="line-clamp-1 text-sm">
							{file?.name ?? file?.meta?.name}
							{#if file?.meta?.size}
								<span class="text-xs text-gray-500">{formatFileSize(file?.meta?.size)}</span>
							{/if}
						</div>
					</div>
				</div>

				<div class="flex items-center gap-2 shrink-0">
					{#if file?.updated_at}
						<Tooltip content={dayjs(file.updated_at * 1000).format('LLLL')}>
							<div>
								{dayjs(file.updated_at * 1000).fromNow()}
							</div>
						</Tooltip>
					{/if}

					{#if file?.user}
						<Tooltip
							content={file?.user?.email ?? $i18n.t('Deleted User')}
							className="flex shrink-0"
							placement="top-start"
						>
							<div class="shrink-0 text-gray-500">
								{$i18n.t('By {{name}}', {
									name: capitalizeFirstLetter(
										file?.user?.name ?? file?.user?.email ?? $i18n.t('Deleted User')
									)
								})}
							</div>
						</Tooltip>
					{/if}
				</div>
			</button>

			<div class="flex items-center">
				{#if file?.id && file?.status !== 'uploading'}
					<Tooltip content={$i18n.t('Download')}>
						<a
							class="p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-850 transition"
							href="{WEBUI_API_BASE_URL}/files/{file.id}/content?attachment=true"
							download={file?.name ?? file?.meta?.name}
							on:click|stopPropagation
						>
							<svg
								xmlns="http://www.w3.org/2000/svg"
								fill="none"
								viewBox="0 0 24 24"
								stroke-width="1.5"
								stroke="currentColor"
								class="size-3.5"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3"
								/>
							</svg>
						</a>
					</Tooltip>
				{/if}

				{#if knowledge?.write_access}
					<Tooltip content={$i18n.t('Delete')}>
						<button
							class="p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-850 transition"
							type="button"
							on:click={() => {
								onDelete(file?.id ?? file?.tempId);
							}}
						>
							<XMark />
						</button>
					</Tooltip>
				{/if}
			</div>
		</div>
	{/each}
</div>
