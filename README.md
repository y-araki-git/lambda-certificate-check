# LambdaでACM証明書の有効期限チェック

簡単なACM証明書の有効期限チェックLambdaです。
コード内で指定した有効期限に達するとSlackチャネルに投稿がきます。

  - WEB_HOOK_URLを変数として渡してください(os.environ['WEB_HOOK_URL']を直接編集してもいいかと)。
  - 有効期限が残り30日、14日、7日になるとWEB HOOLで指定したSlackチャネルに投稿されます。
